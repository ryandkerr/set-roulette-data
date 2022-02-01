import pandas as pd
import sqlite3
import numpy as np
import pdb

from sklearn.cluster import AgglomerativeClustering
from sklearn.decomposition import LatentDirichletAllocation
from scipy.cluster.hierarchy import dendrogram

MTG_MELEE_DB_PATH = "../mtgmelee.db"


class DeckClustering(object):
    def __init__(self, *, db_path, tournament_id, include_lands=False):
        self.tournament_id = tournament_id
        self.conn = sqlite3.connect(db_path)
        self.include_lands = include_lands

    def set_include_lands(self, include_lands):
        self.include_lands = include_lands

    def get_clusters_heirarchical(
        self,
        n_clusters=None,
        distance_threshold=16,
        compute_full_tree=True,
        compute_distances=True,
        **kwargs
    ):
        prepared = self._get_prepared_df()
        model = AgglomerativeClustering(
            n_clusters=n_clusters,
            distance_threshold=distance_threshold,
            compute_full_tree=compute_full_tree,
            compute_distances=compute_distances,
            **kwargs,
        )
        model = model.fit(prepared.to_numpy())
    
        deck_info_df = self._get_deck_info_df()
        out = pd.merge(
            prepared,
            deck_info_df,
            left_on='deck_id',
            right_on='id'
        )
        out['classification'] = model.labels_
        leftmost_cols = ['name', 'title']
        out = out.reindex(columns=(leftmost_cols + list([col for col in out.columns if col not in leftmost_cols])))
        return out, model
    
    def plot_dendrogram(self, *, df, model, **kwargs):
        if df['title'] is not None and df['name'] is not None:
            labels = (df['title'] + ': ' + df['name']).tolist()
        else:
            labels = None
        self._plot_dendrogram(model, labels=labels, orientation="right", **kwargs)

    def get_clusters_lda(self, *, n_components):
        land_clause = f"AND s.type_line NOT LIKE '%Land%'" if not self.include_lands else ""
        query = f"""
        SELECT
            cards.*,
            decks.tournament_id
        FROM cards
        JOIN decks
            ON cards.deck_id = decks.id
        JOIN scryfall_cards s
            ON cards.name = s.name
            {land_clause}
        """

        deck_name_query = """
        SELECT
            id,
            title
        FROM decks
        """

        df = pd.read_sql_query(query, self.conn)
        deck_name_df = pd.read_sql_query(deck_name_query, self.conn)

        tst = df.loc[(df['is_sideboard'] == 0) & (df['tournament_id'] == self.tournament_id)]
        prepared = tst.pivot(
            index='deck_id',
            columns='name',
            values='quantity'
        ).fillna(0)

        model = LatentDirichletAllocation(n_components=n_components, random_state=0)
        model.fit(prepared.to_numpy())
        raw_predictions = model.transform(prepared)

        classifications = [self._classify(row) for row in raw_predictions]
        out = prepared.copy()
        out['classification'] = [x[0] for x in classifications]
        out['p_val'] = [x[1] for x in classifications]
        out = pd.merge(out, deck_name_df, left_on='deck_id', right_on='id')
        out = out.reindex(columns=(['title'] + list([col for col in out.columns if col != 'title'])))
        return out, model

    def get_cluster_summary(self, df):
        cluster_summary = {}
        clusters = np.unique(df['classification'])
        for cluster in clusters:
            colnames = ['classification', 'id', 'name', 'title', 'wins', 'losses']
            s = df[df['classification'] == cluster].drop(colnames, axis=1)
            s = s.sum()[1:].sort_values(ascending=False)
            cluster_summary[cluster] = ', '.join(list(s[0:3].index))
        return cluster_summary

    def get_winrate_matrix(self, df, min_cluster_size=4):
        clean_clusters = self.combine_small_clusters(df, min_cluster_size=min_cluster_size)
        results_df = self._get_results_df()

        cleaned = clean_clusters[['id', 'classification']]
        num_decklists_df = cleaned.groupby('classification').agg('count')
        num_decklists_df = num_decklists_df.rename(columns={'id': 'Num Decks'})
        
        tst = pd.merge(cleaned, results_df, how='left', left_on='id', right_on='player1_deck_id')
        tst = pd.merge(tst, cleaned, how='left', left_on='player2_deck_id', right_on='id', suffixes=('_player1', '_player2'))
        cleaned = tst[['player1_deck_id', 'player2_deck_id', 'classification_player1', 'classification_player2', 'player1_wins']]

        summary = cleaned.groupby(['classification_player1', 'classification_player2']) \
            .agg({'player1_wins': ["count", "sum", "mean"]}) \
            .reindex()
        summary.columns = [col[1] for col in summary.columns.to_flat_index()]
        summary = summary.reset_index()        
        summary['final_col'] = [f'{round(mean*100)}%, {count}' for mean, count in zip(summary['mean'], summary['count'])]
        summary = summary.pivot(
            index='classification_player1',
            columns='classification_player2',
            values='final_col'
        )

        summary = pd.merge(
            summary,
            num_decklists_df,
            how='inner',
            left_index=True,
            right_index=True
        )

        summary2 = cleaned[cleaned['classification_player1'] != cleaned['classification_player2']] \
            .groupby('classification_player1') \
            .agg({'player1_wins': ['count', 'mean']})
        summary2.columns = [col[1] for col in summary2.columns.to_flat_index()]
        summary['Non-Mirror %'] = [f'{round(x*100)}%' for x in summary2['mean']]
        summary['Non-Mirror Matches'] = summary2['count']

        top_cards = self.get_cluster_summary(clean_clusters)
        summary['Top Cards'] = [top_cards[cluster] for cluster in summary.index]
        summary.index.name = 'Deck Cluster'
        return summary

    def combine_small_clusters(self, df, min_cluster_size=4):
        out = df.copy()
        grouped = out.groupby('classification')
        g = grouped.size()

        def classify(x, grouped, min_size): 
            return str(x) if grouped[x] >= min_size else 'Other'

        out['classification'] = [classify(x, g, min_cluster_size) for x in out['classification']]
        return out

    def _classify(self, predictions, min_threshold=.6):
        mx = float('-inf')
        classification = None
        for i, prediction in enumerate(predictions):
            if prediction > mx:
                mx = prediction
                classification = str(i)
                
        if mx < min_threshold:
            classification = 'Other'
        return classification, mx

    def _get_prepared_df(self):
        land_clause = f"AND s.type_line NOT LIKE '%Land%'" if not self.include_lands else ""
        query = f"""
        SELECT
            cards.*,
            decks.tournament_id
        FROM cards
        JOIN decks
            ON cards.deck_id = decks.id
        JOIN scryfall_cards s
            ON cards.name = s.name
            {land_clause}
        """

        df = pd.read_sql_query(query, self.conn)

        tst = df.loc[(df['is_sideboard'] == 0) & (df['tournament_id'] == self.tournament_id)]
        prepared = tst.pivot(
            index='deck_id',
            columns='name',
            values='quantity'
        ).fillna(0)
        return prepared

    def _get_deck_info_df(self):
        deck_name_query = """
        SELECT
            decks.id,
            title,
            players.name
        FROM decks
        JOIN players
            ON decks.player_id = players.id
        """

        results_summary_df = self._get_results_summary_df()
        deck_name_df = pd.read_sql_query(deck_name_query, self.conn)
        deck_info_df = pd.merge(
            deck_name_df,
            results_summary_df,
            left_on="id",
            right_on="id"
        )
        return deck_info_df

    def _get_results_df(self):
        query = """
        SELECT
            player1_deck_id,
            player2_deck_id,
            CASE WHEN winner_id = player1_id THEN 1 ELSE 0 END as player1_wins
        FROM results
        WHERE
            player2_id IS NOT NULL
            
        UNION ALL
        SELECT
            player2_deck_id as player1_deck_id,
            player1_deck_id as player2_deck_id,
            CASE WHEN winner_id = player2_id THEN 1 ELSE 0 END as player1_wins
        FROM results
        WHERE
            player2_id IS NOT NULL
        """

        results_df = pd.read_sql_query(query, self.conn)
        return results_df

    def _get_results_summary_df(self):
        query = """
        WITH a as (
            SELECT
                player1_deck_id,
                player2_deck_id,
                CASE WHEN winner_id = player1_id THEN 1 ELSE 0 END as player1_wins
            FROM results
            WHERE
                player2_id IS NOT NULL
                
            UNION ALL
            SELECT
                player2_deck_id as player1_deck_id,
                player1_deck_id as player2_deck_id,
                CASE WHEN winner_id = player2_id THEN 1 ELSE 0 END as player1_wins
            FROM results
            WHERE
                player2_id IS NOT NULL
        )

        SELECT
            player1_deck_id as id,
            SUM(player1_wins) as wins,
            COUNT(*) - SUM(player1_wins) as losses
        FROM a
        GROUP BY 1
        """

        results_summary_df = pd.read_sql_query(query, self.conn)
        return results_summary_df


    def _plot_dendrogram(self, model, **kwargs):
        # Code from: https://scikit-learn.org/stable/auto_examples/cluster/plot_agglomerative_dendrogram.html
        # Create linkage matrix and then plot the dendrogram

        # create the counts of samples under each node
        counts = np.zeros(model.children_.shape[0])
        n_samples = len(model.labels_)
        for i, merge in enumerate(model.children_):
            current_count = 0
            for child_idx in merge:
                if child_idx < n_samples:
                    current_count += 1  # leaf node
                else:
                    current_count += counts[child_idx - n_samples]
            counts[i] = current_count

        linkage_matrix = np.column_stack([model.children_, model.distances_,
                                        counts]).astype(float)

        # Plot the corresponding dendrogram
        dendrogram(linkage_matrix, **kwargs)


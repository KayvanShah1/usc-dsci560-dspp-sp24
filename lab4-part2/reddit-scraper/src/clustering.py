import pickle

import numpy as np
import pandas as pd
from crud import fetch_posts_embeddings
from database import get_db
from settings import Path, config
from sklearn.cluster import KMeans

db = get_db()


def load_kmeans_model():
    with open(Path.clustering_model, "rb") as f:
        kmeans_model = pickle.load(f)
    return kmeans_model


def train_save_kmeans():
    embeddings = fetch_posts_embeddings(db)
    embeddings = pd.DataFrame([m.model_dump() for m in embeddings])

    X_train = np.stack(embeddings["embedding_array"])

    kmeans_model = KMeans(random_state=config.RANDOM_STATE, n_clusters=config.OPTIMAL_CLUSTERS, n_init="auto")
    kmeans_model.fit(X_train)

    # Save the trained KMeans model using pickle
    with open(Path.clustering_model, "wb") as f:
        pickle.dump(kmeans_model, f)

    return kmeans_model


def infer_clusters(embedding_arrays, kmeans_model):
    # Reshape the embedding arrays to match the input shape expected by the KMeans model
    embedding_arrays_reshaped = np.array(embedding_arrays).reshape(len(embedding_arrays), -1)

    # Predict the clusters for all embedding arrays
    clusters = kmeans_model.predict(embedding_arrays_reshaped)

    return clusters.tolist()

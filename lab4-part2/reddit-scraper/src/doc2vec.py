from crud import get_all_ids_and_content
from database import get_db
from extract import TextCleaner, TextPreprocessor
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from gensim.utils import simple_preprocess
from settings import Path
from tqdm import tqdm

db = get_db()


def preprocess_docs(documents):
    tagged_doc = []
    for doc in tqdm(documents):
        tagged_doc.append(TaggedDocument(simple_preprocess(doc.content), doc.id))
    return tagged_doc


def model_train_save(corpora):
    model = Doc2Vec(vector_size=200, min_count=5, epochs=60)
    model.build_vocab(corpora)
    model.train(corpora, total_examples=model.corpus_count, epochs=model.epochs)
    model.save(Path.embeddings_model)


def load_emb_model():
    return Doc2Vec.load(Path.embeddings_model)


def train_embedding_generation_model():
    documents = get_all_ids_and_content(db)
    documents = preprocess_docs(documents)
    model_train_save(documents)
    return documents


def get_embedding_vector(text, model):
    text = TextCleaner.clean_text(text)
    text = TextPreprocessor.preprocess_text(text)
    text = simple_preprocess(text)
    return model.infer_vector(text)


def add_to_embeddings_table():
    documents = get_all_ids_and_content(db)


from pprint import pprint

model = load_emb_model()
pprint(model.dv)

from flask import Flask, request, jsonify, render_template
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

app = Flask(__name__)

# Load dataset
newsgroups = fetch_20newsgroups(subset='all', remove=('headers', 'footers', 'quotes'))
documents = newsgroups.data
document_metadata = fetch_20newsgroups(subset='all', remove=())  # Keeps all metadata (like headers)

# Convert documents to TF-IDF matrix
vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
tfidf_matrix = vectorizer.fit_transform(documents)

# Apply SVD (LSA) for dimensionality reduction
svd = TruncatedSVD(n_components=100)
lsa_matrix = svd.fit_transform(tfidf_matrix)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    query_vector = vectorizer.transform([query])
    query_lsa = svd.transform(query_vector)

    # Calculate cosine similarity between query and all documents
    similarities = cosine_similarity(query_lsa, lsa_matrix)[0]
    top_indices = similarities.argsort()[-5:][::-1]  # Get top 5 documents

    top_documents = []
    for i in top_indices:
        # Extract metadata (email, subject, organization) from the original documents
        metadata = document_metadata.data[i]
        email_start = metadata.find('From:')
        email_end = metadata.find('\n', email_start)
        subject_start = metadata.find('Subject:')
        subject_end = metadata.find('\n', subject_start)
        org_start = metadata.find('Organization:')
        org_end = metadata.find('\n', org_start)
        
        email = metadata[email_start+5:email_end].strip() if email_start != -1 else "No email found"
        subject = metadata[subject_start+8:subject_end].strip() if subject_start != -1 else "No subject found"
        organization = metadata[org_start+13:org_end].strip() if org_start != -1 else "No organization found"

        full_document = documents[i]  # Extract the full document content
        top_documents.append({
            'email': email,
            'subject': subject,
            'organization': organization,  # Add organization field
            'content': full_document,  # Use 'content' instead of 'snippet'
            'similarity': similarities[i]
        })

    # Prepare data for chart
    chart_data = {'labels': [f'Document {i+1}' for i in range(5)], 'values': [similarities[i] for i in top_indices]}

    return jsonify({'documents': top_documents, 'chart_data': chart_data})




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)

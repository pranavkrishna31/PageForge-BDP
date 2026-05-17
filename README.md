# PageForge-BDP

A lightweight intelligent book recommendation platform built using Flask, MongoDB, and hybrid recommendation system techniques. The system combines content-based filtering, TF-IDF vectorization, cosine similarity, and multi-signal behavioral analytics to generate personalized book recommendations.

---

# Features

## Hybrid Recommendation Engine
Implements a recommendation system using:
- TF-IDF Vectorization
- Cosine Similarity
- Content-Based Filtering
- Behavioral Recommendation Weighting
- Multi-Signal User Interaction Tracking

The engine dynamically adapts recommendations based on:
- Book views
- Cart additions
- Reviews and ratings
- Purchase history

---

## Multi-Signal Behavioral Analytics
Tracks and evaluates:
- Detail page views
- Cart interactions
- Reviews and ratings
- Purchase activity
- Click-through behavior

Each interaction contributes weighted influence to recommendation ranking.

---

## Recommendation Evaluation Metrics
The system includes:
- Precision@K
- Recall@K
- CTR (Click Through Rate)

These metrics are visualized in the admin analytics dashboard.

---

## User Features
- User registration and login
- Personalized recommendations
- Book search and filtering
- Genre-based browsing
- Cart management
- Checkout and order history
- Book reviews and ratings
- Contact/support form

---

## Admin Features
- Recommendation analytics dashboard
- Precision@K and Recall@K tracking
- CTR analytics
- Top seller monitoring
- Inventory management
- Stock updates
- Sales management

---

# Recommendation System Architecture

## 1. Content-Based Filtering

Book metadata is converted into textual vectors using:
- Title
- Author
- Genre
- Description

Example corpus generation:

```python
text = f"""
{book.get('Title', '')}
{book.get('Author', '')}
{book.get('Genre', '')}
{book.get('Description', '')}
"""
```

---

## 2. TF-IDF Vectorization

Textual features are transformed into numerical vectors using:

```python
TfidfVectorizer(stop_words='english')
```

This converts textual book information into weighted vector representations.

---

## 3. Cosine Similarity

Similarity between books is computed using:

```python
cosine_similarity(tfidf_matrix, tfidf_matrix)
```

This identifies books with similar textual characteristics.

---

## 4. Multi-Signal Recommendation Weighting

The recommendation engine incorporates multiple user behavior signals.

### Interaction Weights

| Interaction Type | Weight |
|---|---|
| View | 1 |
| Review | 4 |
| Cart Addition | 5 |
| Purchase | 8 |

Higher-intent actions contribute stronger recommendation influence.

---

# Tech Stack

## Backend
- Flask
- Python

## Database
- MongoDB Atlas
- PyMongo

## Recommendation Technologies
- Scikit-learn
- TF-IDF
- Cosine Similarity

## Frontend
- HTML
- CSS
- JavaScript
- Jinja2 Templates

---

# Project Structure

```bash
PageForge-BDP/
│
├── static/
│   ├── css/
│   │   └── custom.css
│   │
│   ├── js/
│   │   ├── admin.js
│   │   └── user.js
│   │
│   └── images/
│
├── templates/
│   ├── admin.html
│   ├── user.html
│   ├── login.html
│   ├── register.html
│   ├── cart.html
│   ├── checkout.html
│   ├── orders.html
│   ├── contact.html
│   └── book_detail.html
│
├── app.py
├── metrics.py
├── seed_books.py
├── seed_users.py
├── requirements.txt
├── .env
└── README.md
```

---

# Installation

## Clone Repository

```bash
git clone https://github.com/pranavkrishna31/PageForge-BDP.git
cd PageForge-BDP
```

---

## Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file in the root directory.

```env
MONGO_URI=your_mongodb_atlas_connection_string
SECRET_KEY=your_secret_key
```

---

# Run Application

```bash
python app.py
```

Application runs at:

```bash
http://127.0.0.1:5000
```

---

# Seed Database

## Seed Books

```bash
python seed_books.py
```

## Seed Admin Users

```bash
python seed_users.py
```

---

# MongoDB Collections

The application uses:
- books
- users
- reviews
- orders
- sales
- contact_queries
- user_interactions

---

# Recommendation Metrics

## Precision@K

Measures how many recommended books are actually relevant.

Formula:

```text
Precision@K = Relevant Recommended Books / Total Recommended Books
```

---

## Recall@K

Measures how many relevant books were successfully recommended.

Formula:

```text
Recall@K = Relevant Recommended Books / Total Relevant Books
```

---

## CTR (Click Through Rate)

Measures user engagement with displayed books.

Formula:

```text
CTR = Clicks / Impressions
```

---

# Security Notes

- MongoDB credentials stored using environment variables
- Session management handled using Flask secret keys
- Atlas IP whitelisting recommended for production

---

# Future Improvements

- Collaborative Filtering
- Deep Learning Recommendation Models
- Recommendation Caching
- Real-Time Recommendation Updates
- User Preference Embeddings
- Recommendation Explanation Layer

---

# Author

Pranav Krishna

GitHub:
https://github.com/pranavkrishna31/PageForge-BDP

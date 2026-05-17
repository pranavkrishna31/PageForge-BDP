import os
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, render_template, redirect, url_for, flash, session
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
from collections import Counter
from metrics import precision_at_k, recall_at_k, ctr
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/bookapp")
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["bookapp"]

@app.route('/')
def home():

    if session.get('role') == 'admin':
        return redirect(url_for('admin_page'))

    if session.get('role') == 'user':
        return redirect(url_for('user_page'))

    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():

    if session.get('role') == 'admin':
        return redirect(url_for('admin_page'))

    if session.get('role') == 'user':
        return redirect(url_for('user_page'))
    
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            username = data.get('username', '').strip()
            password = data.get('password', '').strip()
            confirm = data.get('confirm', '').strip()
            role = "user"
            if not username or not password or not confirm:
                return jsonify({"status": "error", "message": "All fields are required"}), 400
            if password != confirm:
                return jsonify({"status": "error", "message": "Passwords do not match"}), 400
            if db.users.find_one({"Username": username}):
                return jsonify({"status": "error", "message": "Username already exists"}), 400
            db.users.insert_one({"Username": username, "Password": password, "Role": role})
            return jsonify({"status": "success", "message": "Registration successful!"})
        else:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            confirm = request.form.get('confirm', '').strip()
            role = "user"
            if not username or not password or not confirm:
                flash("All fields are required.", "danger")
                return render_template("register.html")
            if password != confirm:
                flash("Passwords do not match.", "danger")
                return render_template("register.html")
            if db.users.find_one({"Username": username}):
                flash("Username already exists. Please choose another.", "danger")
                return render_template("register.html")
            db.users.insert_one({"Username": username, "Password": password, "Role": role})
            session['username'] = username
            session['role'] = role
            return redirect(url_for('user_page'))
    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():

    if session.get('role') == 'admin':
        return redirect(url_for('admin_page'))

    if session.get('role') == 'user':
        return redirect(url_for('user_page'))
    
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            username = data.get('username', '').strip()
            password = data.get('password', '').strip()
        else:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
        user = db.users.find_one({"Username": username, "Password": password})
        if user:
            session['username'] = user['Username']
            session['role'] = user['Role']
            if request.is_json:
                return jsonify({
                    "status": "success",
                    "role": user['Role'],
                    "redirect": url_for('admin_page' if user['Role']=='admin' else 'user_page')
                })
            flash("Login successful!", "success")
            if user['Role'] == 'admin':
                return redirect(url_for('admin_page'))
            else:
                return redirect(url_for('user_page'))
        else:
            if request.is_json:
                return jsonify({"status": "error", "message": "Invalid username or password"}), 401
            flash('Invalid username or password.', 'danger')
            return render_template('login.html')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/admin')
def admin_page():

    if session.get('role') != 'admin':

        flash(
            'You must be an admin.',
            'danger'
        )

        return redirect(url_for('login'))

    # ====================================
    # FETCH BOOKS
    # ====================================

    books = list(

        db.books.find(
            {},
            {"_id": 0}
        )

    )

    # ====================================
    # RECOMMENDED BOOKS
    # ====================================

    interaction_counter = Counter()

    interactions = list(

        db.user_interactions.find({})

    )

    for interaction in interactions:

        book_id = interaction.get("BookID")

        interaction_type = interaction.get(

            "InteractionType"

        )

        weight = 1

        if interaction_type == "view":

            weight = 1

        elif interaction_type == "review":

            weight = 4

        elif interaction_type == "cart":

            weight = 5

        elif interaction_type == "purchase":

            weight = 8

        interaction_counter[book_id] += weight

    recommended_books = [

        book_id

        for book_id, score in interaction_counter.most_common(5)

    ]

    # ====================================
    # RELEVANT BOOKS
    # ====================================

    orders = list(

        db.orders.find(
            {},
            {"Books.BookID": 1}
        )

    )

    relevant_books = []

    for order in orders:

        for book in order.get('Books', []):

            if 'BookID' in book:

                relevant_books.append(

                    book['BookID']

                )

    relevant_books = list(

        set(relevant_books)

    )

    # ====================================
    # PRECISION / RECALL
    # ====================================

    k = 5

    precision = precision_at_k(

        recommended_books,

        relevant_books,

        k

    )

    recall = recall_at_k(

        recommended_books,

        relevant_books,

        k

    )

    precision = round(

        precision * 100,

        2

    )

    recall = round(

        recall * 100,

        2

    )

    # ====================================
    # CTR CALCULATION
    # ====================================

    for book in books:

        click_count = (

            book.get(
                "ClickCount",
                0
            )

            +

            book.get(
                "DetailViews",
                0
            )

        )

        show_count = book.get(

            "ShowCount",

            1

        )

        ctr_value = 0

        if show_count > 0:

            ctr_value = (

                click_count /

                show_count

            ) * 100

        book["CTR"] = round(

            ctr_value,

            2

        )

    # ====================================
    # AVG CTR
    # ====================================

    avg_ctr = 0

    if books:

        avg_ctr = round(

            sum(

                b["CTR"]

                for b in books

            ) / len(books),

            2

        )

    # ====================================
    # TOP SELLERS
    # ====================================

    thirty_days_ago = (

        datetime.utcnow()

        - timedelta(days=30)

    )

    recent_orders = list(

        db.orders.find(

            {

                "Date": {

                    "$gte": thirty_days_ago

                }

            },

            {

                "Books.Title": 1

            }

        )

    )

    sales_counter = Counter()

    for order in recent_orders:

        for book in order.get("Books", []):

            if "Title" in book:

                sales_counter[

                    book["Title"]

                ] += 1

    top_sellers = sales_counter.most_common(10)

    seller_labels = [

        title

        for title, count in top_sellers

    ]

    seller_values = [

        count

        for title, count in top_sellers

    ]

    # ====================================
    # TOP CTR BOOKS
    # ====================================

    top_ctr_books = sorted(

        books,

        key=lambda x: x.get(

            "CTR",

            0

        ),

        reverse=True

    )[:5]

    # ====================================
    # RENDER
    # ====================================

    return render_template(

        'admin.html',

        books=books,

        precision=precision,

        recall=recall,

        k=k,

        avg_ctr=avg_ctr,

        seller_labels=seller_labels,

        seller_values=seller_values,

        recommended_books=recommended_books,

        relevant_books=relevant_books,

        top_ctr_books=top_ctr_books

    )
@app.route('/user', methods=['GET', 'POST'])
def user_page():

    if session.get('role') != 'user':

        flash('Please login as user.', 'danger')

        return redirect(url_for('login'))

    q = request.args.get('q', '').strip()

    genre = request.args.get('genre')

    sort = request.args.get('sort', 'price')

    query = {}

    # =========================
    # SEARCH
    # =========================

    if q:

        query['$or'] = [

            {
                'Title': {
                    '$regex': q,
                    '$options': 'i'
                }
            },

            {
                'Author': {
                    '$regex': q,
                    '$options': 'i'
                }
            }

        ]

    # =========================
    # GENRE FILTER
    # =========================

    if genre:

        query['Genre'] = genre

    # =========================
    # SORTING
    # =========================

    sort_key = 'Price' if sort == 'price' else 'RatingMean'

    books = list(

        db.books.find(
            query,
            {"_id": 0}
        ).sort(
            sort_key,
            -1 if sort == 'rating' else 1
        )

    )

    # =========================
    # GENRES
    # =========================

    genres = db.books.distinct("Genre")

    # =========================
    # TRACK SHOW COUNT
    # =========================

    for book in books:

        db.books.update_one(

            {'BookID': book['BookID']},

            {
                '$inc': {
                    'ShowCount': 1
                }
            }
        )

    # =========================
    # FETCH ALL BOOKS
    # =========================

    all_books = list(

        db.books.find({}, {"_id": 0})

    )

    recommended_books = []

    if len(all_books) > 1:

        # =========================
        # CREATE TEXT CORPUS
        # =========================

        corpus = []

        for book in all_books:

            text = f"""

            {book.get('Title', '')}

            {book.get('Author', '')}

            {book.get('Genre', '')}

            {book.get('Description', '')}

            """

            corpus.append(text)

        # =========================
        # TF-IDF VECTORIZATION
        # =========================

        tfidf = TfidfVectorizer(

            stop_words='english'

        )

        tfidf_matrix = tfidf.fit_transform(corpus)

        # =========================
        # COSINE SIMILARITY
        # =========================

        similarity_matrix = cosine_similarity(

            tfidf_matrix,
            tfidf_matrix

        )

        # =========================
        # USER INTERACTIONS
        # =========================

        interactions = list(

            db.user_interactions.find({

                "Username": session.get("username")

            })

        )

        # =========================
        # INTERACTION WEIGHTS
        # =========================

        interaction_weights = {

            "view": 1,

            "review": 4,

            "cart": 5,

            "purchase": 8

        }

        weighted_scores = {}

        interacted_book_ids = set()

        for interaction in interactions:

            book_id = interaction.get("BookID")

            interaction_type = interaction.get(

                "InteractionType"

            )

            weight = interaction_weights.get(

                interaction_type,

                1

            )

            # EXTRA BOOST FOR HIGH RATINGS

            if interaction_type == "review":

                rating_value = interaction.get(

                    "InteractionValue",

                    0

                )

                weight += rating_value

            interacted_book_ids.add(book_id)

            interacted_index = next(

                (

                    i for i, b in enumerate(all_books)

                    if b["BookID"] == book_id

                ),

                None

            )

            if interacted_index is not None:

                similarity_scores = list(

                    enumerate(

                        similarity_matrix[interacted_index]

                    )

                )

                for idx, similarity_score in similarity_scores:

                    candidate_book = all_books[idx]

                    candidate_id = candidate_book["BookID"]

                    if candidate_id == book_id:

                        continue

                    weighted_scores[candidate_id] = (

                        weighted_scores.get(

                            candidate_id,

                            0

                        )

                        +

                        (similarity_score * weight)

                    )

        # =========================
        # SORT FINAL SCORES
        # =========================

        sorted_books = sorted(

            weighted_scores.items(),

            key=lambda x: x[1],

            reverse=True

        )

        for book_id, score in sorted_books:

            book = next(

                (

                    b for b in all_books

                    if b["BookID"] == book_id

                ),

                None

            )

            if book:

                recommended_books.append(book)

            if len(recommended_books) >= 5:

                break

    # =========================
    # FALLBACK RECOMMENDATIONS
    # =========================

    if not recommended_books:

        recommended_books = sorted(

            all_books,

            key=lambda x: x.get("RatingMean", 0),

            reverse=True

        )[:5]

    return render_template(

        "user.html",

        books=books,

        genres=genres,

        recommended_books=recommended_books

    )
# =========================
# BOOK DETAIL PAGE
# =========================

@app.route('/book/<int:book_id>', methods=['GET', 'POST'])
def book_detail(book_id):

    if session.get('role') != 'user':

        flash(
            'Please login as user.',
            'danger'
        )

        return redirect(url_for('login'))

    # =========================
    # SUBMIT REVIEW
    # =========================

    if request.method == 'POST':

        rating = int(

            request.form.get('rating')

        )

        review_text = request.form.get(

            'review_text',
            ''

        ).strip()

        # =========================
        # SAVE REVIEW
        # =========================

        db.reviews.insert_one({

            "BookID": book_id,

            "Username": session.get('username'),

            "Rating": rating,

            "ReviewText": review_text,

            "CreatedAt": datetime.utcnow()

        })

        # =========================
        # STORE REVIEW INTERACTION
        # =========================

        db.user_interactions.insert_one({

            "Username": session.get("username"),

            "BookID": book_id,

            "InteractionType": "review",

            "InteractionValue": rating,

            "Timestamp": datetime.utcnow()

        })

        # =========================
        # UPDATE DYNAMIC RATING
        # =========================

        book_data = db.books.find_one({

            "BookID": book_id

        })

        current_mean = book_data.get(

            "RatingMean",

            0

        )

        current_count = book_data.get(

            "RatingCount",

            0

        )

        new_mean = (

            (

                current_mean * current_count

            )

            + rating

        ) / (current_count + 1)

        db.books.update_one(

            {

                "BookID": book_id

            },

            {

                "$set": {

                    "RatingMean": round(

                        new_mean,

                        2

                    )

                },

                "$inc": {

                    "RatingCount": 1

                }

            }

        )

        flash(

            'Review submitted successfully.',

            'success'

        )

        return redirect(

            url_for(

                'book_detail',

                book_id=book_id

            )

        )

    # =========================
    # FETCH BOOK
    # =========================

    book = db.books.find_one(

        {

            'BookID': book_id

        },

        {

            '_id': 0

        }

    )

    if not book:

        flash(

            'Book not found.',

            'danger'

        )

        return redirect(

            url_for('user_page')

        )

    # =========================
    # TRACK VIEWS
    # =========================

    db.books.update_one(

        {

            'BookID': book_id

        },

        {

            '$inc': {

                'DetailViews': 1

            }

        }

    )

    # =========================
    # STORE VIEW INTERACTION
    # =========================

    db.user_interactions.insert_one({

        "Username": session.get("username"),

        "BookID": book_id,

        "InteractionType": "view",

        "Timestamp": datetime.utcnow()

    })

    # =========================
    # RELATED BOOKS
    # =========================

    related_books = list(

        db.books.find(

            {

                'Genre': book['Genre'],

                'BookID': {

                    '$ne': book_id

                }

            },

            {

                '_id': 0

            }

        ).sort(

            'RatingMean',

            -1

        ).limit(4)

    )

    # =========================
    # REVIEWS
    # =========================

    reviews = list(

        db.reviews.find(

            {

                'BookID': book_id

            },

            {

                '_id': 0

            }

        ).sort(

            'CreatedAt',

            -1

        )

    )

    return render_template(

        'book_detail.html',

        book=book,

        related_books=related_books,

        reviews=reviews

    )
    
# =========================
# ADD TO CART
# =========================

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():

    if session.get('role') != 'user':

        flash(
            'Please login as user.',
            'danger'
        )

        return redirect(url_for('login'))

    book_id = request.form.get('book_id')

    if not book_id:

        return redirect(
            request.referrer or url_for('user_page')
        )

    cart = session.get('cart', [])

    # =========================
    # PREVENT DUPLICATES
    # =========================

    if str(book_id) not in [str(id) for id in cart]:

        cart.append(str(book_id))

        # =========================
        # STORE CART INTERACTION
        # =========================

        db.user_interactions.insert_one({

            "Username": session.get("username"),

            "BookID": int(book_id),

            "InteractionType": "cart",

            "Timestamp": datetime.utcnow()

        })

    session['cart'] = cart

    session.modified = True

    flash(
        'Book added to cart.',
        'success'
    )

    return redirect(
        request.referrer or url_for('user_page')
    )


# =========================
# CART PAGE
# =========================

@app.route('/cart')
def cart_page():

    if session.get('role') != 'user':

        flash(
            'Please login as user.',
            'danger'
        )

        return redirect(url_for('login'))

    # GET CART IDS
    cart_ids = [

        int(id)

        for id in session.get('cart', [])

    ]

    # FETCH VALID BOOKS ONLY
    books = list(

        db.books.find(

            {

                'BookID': {

                    '$in': cart_ids

                }

            },

            {

                '_id': 0

            }

        )

    )

    # =========================
    # SYNC SESSION CART
    # =========================

    valid_ids = [

        str(book['BookID'])

        for book in books

    ]

    session['cart'] = valid_ids

    session.modified = True

    # =========================
    # TOTAL
    # =========================

    total = round(

        sum(

            book.get('Price', 0)

            for book in books

        ),

        2

    )

    return render_template(

        'cart.html',

        books=books,

        total=total

    )


# =========================
# DELETE FROM CART
# =========================

@app.route('/delete_from_cart', methods=['POST'])
def delete_from_cart():

    if session.get('role') != 'user':

        return redirect(url_for('login'))

    book_id = request.form.get('book_id')

    cart = session.get('cart', [])

    # REMOVE BOOK
    cart = [

        str(id)

        for id in cart

        if str(id) != str(book_id)

    ]

    session['cart'] = cart

    session.modified = True

    flash(
        'Book removed from cart.',
        'success'
    )

    return redirect(url_for('cart_page'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout_page():

    if session.get('role') != 'user':

        flash('Please login as user.', 'danger')

        return redirect(url_for('login'))

    cart_ids = [

        int(id)

        for id in session.get('cart', [])

    ]

    books = list(

        db.books.find(

            {

                'BookID': {

                    '$in': cart_ids

                }

            },

            {

                '_id': 0

            }

        )

    )

    total = sum(

        book.get('Price', 0)

        for book in books

    )

    # =========================
    # PLACE ORDER
    # =========================

    if request.method == 'POST':

        name = request.form.get(

            'name',
            ''

        ).strip()

        address = request.form.get(

            'address',
            ''

        ).strip()

        phone = request.form.get(

            'phone',
            ''

        ).strip()

        payment_method = request.form.get(

            'payment_method'

        )

        # =========================
        # TRACK PURCHASE SIGNALS
        # =========================

        for book in books:

            # CTR CLICK TRACKING

            db.books.update_one(

                {

                    'BookID': book['BookID']

                },

                {

                    '$inc': {

                        'ClickCount': 1

                    }

                }

            )

            # =========================
            # STORE PURCHASE INTERACTION
            # =========================

            db.user_interactions.insert_one({

                "Username": session.get("username"),

                "BookID": book['BookID'],

                "InteractionType": "purchase",

                "InteractionValue": book.get(

                    "Price",

                    0

                ),

                "Timestamp": datetime.utcnow()

            })

        # =========================
        # SAVE ORDER
        # =========================

        db.orders.insert_one({

            "Username": session.get('username'),

            "Name": name,

            "Address": address,

            "Phone": phone,

            "Books": books,

            "Total": total,

            "PaymentMethod": payment_method,

            "Date": datetime.utcnow()

        })

        # CLEAR CART

        session['cart'] = []

        session.modified = True

        flash(

            'Order placed successfully!',

            'success'

        )

        return redirect(

            url_for('orders_page')

        )

    return render_template(

        'checkout.html',

        books=books,

        total=total

    )


# =========================
# ORDERS PAGE
# =========================

@app.route('/orders')
def orders_page():

    if session.get('role') != 'user':

        return redirect(

            url_for('login')

        )

    orders = list(

        db.orders.find(

            {

                'Username': session.get('username')

            },

            {

                '_id': 0

            }

        ).sort(

            'Date',

            -1

        )

    )

    return render_template(

        'orders.html',

        orders=orders

    )
# =========================
# CONTACT PAGE
# =========================

@app.route('/contact', methods=['GET', 'POST'])
def contact_page():

    if request.method == 'POST':

        username = request.form.get('username', '').strip()

        email = request.form.get('email', '').strip()

        subject = request.form.get('subject', '').strip()

        query_message = request.form.get('query_message', '').strip()

        db.contact_queries.insert_one({

            "Username": username,

            "Email": email,

            "Subject": subject,

            "QueryMessage": query_message,

            "CreatedAt": datetime.utcnow()

        })

        flash(
    'Query sent successfully. You can expect a response within 24–48 hours.',
    'success'
)
        return redirect(url_for('contact_page'))

    return render_template('contact.html')

@app.route('/update_stock', methods=['POST'])
def update_stock():

    if session.get('role') != 'admin':

        return jsonify({

            "message": "Unauthorized"

        }), 403

    data = request.get_json()

    book_id = data.get('book_id')

    stock = data.get('stock')

    book = db.books.find_one({

        "BookID": book_id

    })

    if not book:

        return jsonify({

            "message": "Book not found"

        }), 404

    db.books.update_one(

        {"BookID": book_id},

{"$set": {"StockAvailable": stock}}
    )

    return jsonify({

        "message": "Stock updated successfully"

    })


@app.route('/add_sale', methods=['POST'])
def add_sale():

    if session.get('role') != 'admin':

        return jsonify({

            "message": "Unauthorized"

        }), 403

    data = request.get_json()

    book_id = data.get('book_id')

    units = int(data.get('units'))

    date = data.get('date')

    book = db.books.find_one({

        "BookID": book_id

    })

    if not book:

        return jsonify({

            "message": "Book not found"

        }), 404

    current_stock = book.get(

        "StockAvailable",

        0

    )

    # PREVENT NEGATIVE STOCK

    if units > current_stock:

        return jsonify({

            "message": f"Only {current_stock} items left in stock"

        }), 400

    # INSERT SALE

    db.sales.insert_one({

        "BookID": book_id,

        "Title": book['Title'],

        "Units": units,

        "Date": date

    })

    # REDUCE INVENTORY

    db.books.update_one(

        {

            "BookID": book_id

        },

        {

            "$inc": {

                "StockAvailable": -units

            }

        }

    )

    return jsonify({

        "message": "Sale added and inventory updated"

    })
# =========================
# RUN APP
# =========================

if __name__ == "__main__":

    app.run(
        debug=False,
        port=5000
    )
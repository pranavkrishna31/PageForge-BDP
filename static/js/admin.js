async function requestJSON(url, options = {}) {

    const response = await fetch(url, options);

    const data = await response.json();

    if (!response.ok) {

        throw new Error(

            data.message || 'Something went wrong'

        );
    }

    return data;
}

/* =========================
   ADD SALE
========================= */

document.getElementById('btn-add-sale').onclick = async () => {

    const bookId = parseInt(

        document.getElementById('sale-book').value

    );

    const units = parseInt(

        document.getElementById('sale-units').value

    );

    const date = document.getElementById('sale-date').value;

    const msg = document.getElementById('sale-msg');

    try {

        const result = await requestJSON(

            '/add_sale',

            {

                method: 'POST',

                headers: {

                    'Content-Type': 'application/json'

                },

                body: JSON.stringify({

                    book_id: bookId,

                    units: units,

                    date: date

                })

            }

        );

        msg.innerHTML = `

            <div class="alert alert-success mt-3">

                ${result.message}

            </div>

        `;

        setTimeout(() => {

            location.reload();

        }, 1000);

    } catch (err) {

        msg.innerHTML = `

            <div class="alert alert-danger mt-3">

                ${err.message}

            </div>

        `;
    }
};

/* =========================
   UPDATE STOCK
========================= */

document.getElementById('btn-update-stock').onclick = async () => {

    const bookId = parseInt(

        document.getElementById('up-book').value

    );

    const stock = parseInt(

        document.getElementById('up-stock').value

    );

    const msg = document.getElementById('up-msg');

    try {

        const result = await requestJSON(

            '/update_stock',

            {

                method: 'POST',

                headers: {

                    'Content-Type': 'application/json'

                },

                body: JSON.stringify({

                    book_id: bookId,

                    stock: stock

                })

            }

        );

        msg.innerHTML = `

            <div class="alert alert-success mt-3">

                ${result.message}

            </div>

        `;

        setTimeout(() => {

            location.reload();

        }, 1000);

    } catch (err) {

        msg.innerHTML = `

            <div class="alert alert-danger mt-3">

                ${err.message}

            </div>

        `;
    }
};
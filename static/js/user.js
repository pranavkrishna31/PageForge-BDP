/* =========================
   TOAST NOTIFICATION
========================= */

function showToast(message) {

    const toast = document.createElement('div');

    toast.className = 'cart-toast';

    toast.innerText = message;

    document.body.appendChild(toast);

    setTimeout(() => {

        toast.classList.add('show');

    }, 100);

    setTimeout(() => {

        toast.classList.remove('show');

        setTimeout(() => {

            toast.remove();

        }, 400);

    }, 2500);
}

/* =========================
   ADD TO CART
========================= */

document.querySelectorAll('.add-cart-form').forEach(form => {

    form.addEventListener('submit', async function(e) {

        e.preventDefault();

        const formData = new FormData(form);

        try {

            const response = await fetch(

                '/add_to_cart',

                {

                    method: 'POST',

                    body: formData

                }

            );

            if (response.ok) {

                showToast('Book added to cart');

                const badge = document.querySelector('.cart-count');

                if (badge) {

                    let count = parseInt(

                        badge.innerText || 0

                    );

                    badge.innerText = count + 1;
                }

            }

        } catch (err) {

            console.error(err);
        }
    });
});

/* =========================
   SMOOTH SCROLL PRESERVE
========================= */

window.history.scrollRestoration = 'manual';
function changeQuantity(productId, change) {
    const qtySpan = document.getElementById(`quantity-${productId}`);
    let currentQty = parseInt(qtySpan.innerText);
    const newQty = currentQty + change;

    if (newQty >= 1) {
        qtySpan.innerText = newQty;

        // Show the update button
        const updateBtn = document.getElementById(`update-btn-${productId}`);
        updateBtn.style.display = "inline-block";
    }
}

function submitQuantityUpdate(productId) {
    const newQty = parseInt(document.getElementById(`quantity-${productId}`).innerText);

    fetch('/update_quantity', {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: newQty
        })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        document.getElementById(`update-btn-${productId}`).style.display = "none"; // Hide after update

        // Update subtotal + total dynamically
        updateCheckoutTotals();
    })
    .catch(err => {
        console.error("Error updating quantity:", err);
    });
}

function updateCheckoutTotals() {
    const itemElements = document.querySelectorAll('.price');
    let subtotal = 0;
    let totalItems = 0;

    itemElements.forEach(priceEl => {
        const productId = priceEl.id.split('-')[1];
        const unitPrice = parseFloat(priceEl.dataset.price);
        const quantity = parseInt(document.getElementById(`quantity-${productId}`).innerText);
        subtotal += unitPrice * quantity;
        totalItems += quantity;
    });

    const tax = 5.00;
    const convenience = 1.00;
    const total = subtotal + tax + convenience;

    //  Update the values in the DOM
    document.querySelector('.checkout-summary').innerHTML = `
        <h2>Order Summary</h2>
        <p>Subtotal: $${subtotal.toFixed(2)}</p>
        <p>Tax: $${tax.toFixed(2)}</p>
        <p>Convenience Fee: $${convenience.toFixed(2)}</p>
        <hr />
        <p class="total-amount">Total: $${total.toFixed(2)}</p>
    `;

    const itemCountEl = document.getElementById("cart-total-items");
    const cartCountText = document.getElementById("cart-count-text");

    if (itemCountEl && cartCountText) {
        itemCountEl.innerText = totalItems;

        const plural = totalItems === 1 ? "item" : "items"; 
        cartCountText.innerHTML = `🛒 You have <span id="cart-total-items">${totalItems}</span> ${plural} in your cart`;
    }
}


function removeItem(productId) {
    if (!confirm("Are you sure you want to remove this item from your cart?")) return;

    fetch('/remove_from_cart', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ product_id: productId })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);

        // Remove the item from the DOM
        const itemElement = document.getElementById(`cart-item-${productId}`);
        if (itemElement) itemElement.remove();

        // Update totals
        updateCheckoutTotals();

        // Now check if any items remain
        const remainingItems = document.querySelectorAll('.cart-item');
        if (remainingItems.length === 0) {
            const cartItemsSection = document.querySelector('.cart-items');

            // Replace entire cart section with empty message
            cartItemsSection.innerHTML = `
                <h2>Items</h2>
                <p class="empty-cart">You don't have any items in your cart.</p>
            `;
        }
    })
    .catch(err => {
        console.error("Error removing item:", err);
    });
}

function openModal(id) {
    document.getElementById(id).style.display = 'flex';
}

function closeModal(id) {
    document.getElementById(id).style.display = 'none';
}

let personalInfo = {};
let paymentInfo = {};

function storePersonalInfo() {
    personalInfo = {
        first_name: document.getElementById('first-name').value,
        last_name: document.getElementById('last-name').value,
        address: document.getElementById('address').value,
        state: document.getElementById('state').value,
        zip: document.getElementById('zip').value
    };
    closeModal('personalModal');
}

function storePaymentInfo() {
    paymentInfo = {
        cc_first_name: document.getElementById('cc-first-name').value,
        cc_last_name: document.getElementById('cc-last-name').value,
        cc_address: document.getElementById('cc-address').value,
        cc_number: document.getElementById('cc-number').value,
        cc_exp: document.getElementById('cc-exp').value,
        cc_cvv: document.getElementById('cc-cvv').value
    };
    closeModal('paymentModal');
}

function confirmOrder() {
    const orderData = {
        personal: personalInfo,
        payment: paymentInfo,
        cart: getCartData() // Optional: if you want to include cart
    };

    fetch('/place_order', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(orderData)
    })
    .then(res => res.json())
    .then(data => {
        showSuccessPopup(data.orderNumber);
    })
    .catch(err => console.error("Order failed", err));
}






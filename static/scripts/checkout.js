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

        //  Remove the item from DOM
        const itemElement = document.getElementById(`cart-item-${productId}`);
        if (itemElement) itemElement.remove();

        updateCheckoutTotals(); // 👈 Update subtotal/total after removal
    })
    .catch(err => {
        console.error("Error removing item:", err);
    });
}


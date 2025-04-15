// Made by Ahmed Sherwani
// Enable/disable "Add to Cart" button based on quantity
function updateQuantity(productId, change) {
    const quantitySpan = document.getElementById(`quantity-${productId}`);
    let currentQty = parseInt(quantitySpan.innerText);
    const newQty = currentQty + change;

    if (newQty >= 0) {
        quantitySpan.innerText = newQty;

        // Enable "Add to Cart" button if quantity > 0
        const addToCartBtn = document.getElementById(`add-to-cart-${productId}`);
        addToCartBtn.disabled = newQty === 0;
    }
}

// For now, just simulate adding to cart
function addToCart(productId, productName) {
    const quantity = parseInt(document.getElementById(`quantity-${productId}`).innerText);

    if (quantity > 0) {
        fetch('/add_to_cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                product_id: productId,
                quantity: quantity
            })
        })
        .then(response => response.json())
        .then(data => {
            alert(`Added ${quantity} of ${productName} to your cart!`);

            const badge = document.getElementById("cart-count");
            if (badge) {
                const currentCount = parseInt(badge.innerText);
                const newCount = currentCount + quantity;
                badge.innerText = newCount;
                badge.style.display = "inline-block";
            }

            document.getElementById(`quantity-${productId}`).innerText = "0";
            document.getElementById(`add-to-cart-${productId}`).disabled = true;
        })
        .catch(error => {
            console.error('Error adding to cart:', error);
        });
    }
}

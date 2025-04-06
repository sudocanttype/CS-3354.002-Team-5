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
function addToCart(productId) {
    const quantity = parseInt(document.getElementById(`quantity-${productId}`).innerText);

    if (quantity > 0) {
        alert(`Added ${quantity} of product ${productId} to your cart!`);

        // Reset quantity and disable button
        document.getElementById(`quantity-${productId}`).innerText = "0";
        document.getElementById(`add-to-cart-${productId}`).disabled = true;
    }
}

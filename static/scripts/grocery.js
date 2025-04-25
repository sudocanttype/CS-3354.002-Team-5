// Made by Ahmed Sherwani
// Enable/disable "Add to Cart" button based on quantity
function updateQuantity(productId, change) {
    const quantitySpan = document.getElementById(`quantity-${productId}`);
    let currentQty = parseInt(quantitySpan.innerText);
    const newQty = currentQty + change;

    // Limit: quantity must be between 0 and 5
    if (newQty >= 0 && newQty <= 5) {
        quantitySpan.innerText = newQty;

        // Enable/disable Add to Cart button
        const addToCartBtn = document.getElementById(`add-to-cart-${productId}`);
        addToCartBtn.disabled = newQty === 0;
    } else if (newQty > 5) {
        alert("You can only add up to 5 of each item.");
    }

}


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

            // Only fetch updated cart count AFTER item is successfully added
            fetch('/cart')
                .then(res => res.json())
                .then(cartData => {
                    const items = cartData.items || [];
                    const totalCount = items.reduce((sum, item) => sum + Number(item.quantity), 0);

                    const badge = document.getElementById("cart-count");
                    badge.innerText = totalCount;
                    badge.style.display = totalCount > 0 ? "inline-block" : "none";
                });

            // Reset quantity and disable button
            document.getElementById(`quantity-${productId}`).innerText = "0";
            document.getElementById(`add-to-cart-${productId}`).disabled = true;
        })
        .catch(error => {
            console.error('Error adding to cart:', error);
        });
    }
}


function updateCartCount() {
  fetch("/cart")
    .then(res => res.json())
    .then(data => {
      const badge = document.getElementById("cart-count");
      const items = data.items || [];
      const totalCount = items.reduce((sum, item) => sum + item.quantity, 0); // ✅ fixed
      badge.innerText = totalCount;
      badge.style.display = totalCount > 0 ? "inline-block" : "none";
    })
    .catch(err => {
      console.error("Error fetching cart data:", err);
    });
}


function updateCartBadge() {
  fetch('/cart')
    .then(res => res.json())
    .then(data => {
      const items = data.items || [];
      const totalCount = items.reduce((sum, item) => sum + Number(item.quantity), 0);
      const badge = document.getElementById("cart-count");

      if (badge) {
        badge.innerText = totalCount;
        badge.style.display = totalCount > 0 ? "inline-block" : "none";
      }
    })
    .catch(err => {
      console.error("Error fetching cart data:", err);
    });
}




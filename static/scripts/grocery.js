// Made by Ahmed Sherwani
// Enable/disable "Add to Cart" button based on quantity
function updateQuantity(productId, change) {
    const quantitySpan = document.getElementById(`quantity-${productId}`);
    let currentQty = parseInt(quantitySpan.innerText);
    const newQty = currentQty + change;

    // Limit: quantity must be between 0 and 5
    if (newQty >= 0 && newQty <= 15) {
        quantitySpan.innerText = newQty;

        // Enable/disable Add to Cart button
        const addToCartBtn = document.getElementById(`add-to-cart-${productId}`);
        addToCartBtn.disabled = newQty === 0;
    } else if (newQty > 5) {
        alert("You can only add up to 15 of each item.");
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

// Search functionality
function searchProducts() {
  const searchInput = document.getElementById('search-input');
  const searchTerm = searchInput.value.toLowerCase().trim();
  const items = document.querySelectorAll('.item');
  const itemsContainer = document.querySelector('.items-container');
  let matchFound = false;

  // Remove existing no results message if it exists
  const existingNoResults = document.getElementById('no-results-message');
  if (existingNoResults) {
    existingNoResults.remove();
  }

  items.forEach(item => {
    const productName = item.querySelector('h3').textContent.toLowerCase();
    // Get all paragraphs (description, price, etc.)
    const paragraphs = item.querySelectorAll('p');
    let productText = productName;

    // Combine all text content from paragraphs
    paragraphs.forEach(p => {
      productText += ' ' + p.textContent.toLowerCase();
    });

    // Check if product name or any paragraph text contains the search term
    if (productText.includes(searchTerm)) {
      item.style.display = 'block';
      matchFound = true;
    } else {
      item.style.display = 'none';
    }
  });

  // Show a message if no results found
  if (!matchFound && searchTerm !== '') {
    const noResultsMessage = document.createElement('div');
    noResultsMessage.id = 'no-results-message';
    noResultsMessage.style.width = '100%';
    noResultsMessage.style.display = 'flex';
    noResultsMessage.style.justifyContent = 'center';
    noResultsMessage.style.gridColumn = '1 / -1'; // Make it span all columns in the grid
    noResultsMessage.innerHTML = `
      <div style="text-align: center; padding: 30px; width: 100%;">
        <h3>No products found matching "${searchTerm}"</h3>
        <p>Try a different search term or browse all products.</p>
      </div>
    `;
    itemsContainer.appendChild(noResultsMessage);
  }
}

// Function to clear search and reset product display
function clearSearch() {
  const searchInput = document.getElementById('search-input');
  const clearButton = document.getElementById('clear-search');

  // Clear the input field
  searchInput.value = '';

  // Hide the clear button
  clearButton.style.display = 'none';

  // Reset the product display
  searchProducts();

  // Focus back on the search input
  searchInput.focus();
}

// Initialize search functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  const searchInput = document.getElementById('search-input');
  const searchButton = document.getElementById('search-button');
  const clearButton = document.getElementById('clear-search');

  // Search when button is clicked
  if (searchButton) {
    searchButton.addEventListener('click', searchProducts);
  }

  // Clear search when clear button is clicked
  if (clearButton) {
    clearButton.addEventListener('click', clearSearch);
  }

  // Search input event handlers
  if (searchInput) {
    // Show/hide clear button based on input content
    searchInput.addEventListener('input', function() {
      if (this.value.trim() !== '') {
        clearButton.style.display = 'block';
      } else {
        clearButton.style.display = 'none';
      }
    });

    // Search when Enter key is pressed
    searchInput.addEventListener('keyup', function(event) {
      if (event.key === 'Enter') {
        searchProducts();
      }

      // Real-time search as user types
      searchProducts();
    });
  }
});

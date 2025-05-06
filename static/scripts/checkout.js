function changeQuantity(productId, change) {
    const qtySpan = document.getElementById(`quantity-${productId}`);
    let currentQty = parseInt(qtySpan.innerText);
    const newQty = currentQty + change;

    // Limit: between 1 and 5 items only
    if (newQty >= 1 && newQty <= 15) {
        qtySpan.innerText = newQty;

        // Show the update button
        const updateBtn = document.getElementById(`update-btn-${productId}`);
        updateBtn.style.display = "inline-block";
    } else if (newQty > 5) {
        alert("You can only add up to 15 of each item.");
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
    document.body.style.overflow = 'hidden';
}

function closeModal(id) {
    document.getElementById(id).style.display = 'none';
    document.body.style.overflow = '';

    // Reset payment button state if closing payment modal
    if (id === 'paymentModal') {
        const submitButton = document.getElementById("submit-payment");
        if (submitButton) {
            submitButton.disabled = false;
            submitButton.textContent = "Confirm Payment";
        }


        const paymentError = document.getElementById('payment-error');
        if (paymentError) {
            paymentError.style.display = 'none';
        }

        // Clean up Stripe Elements if they exist
        if (paymentElement) {
            paymentElement.unmount();
            paymentElement = null;
        }
        if (elements) {
            elements = null;
        }

        // Reset the payment element container
        const paymentElementContainer = document.getElementById('payment-element');
        if (paymentElementContainer) {
            paymentElementContainer.innerHTML = '';
        }
    }
}

let personalInfo = {};
let paymentInfo = {};
let stripe;
let elements;
let paymentElement;
let clientSecret;

function storePersonalInfo() {
    personalInfo = {
        first_name: document.getElementById('first-name').value,
        last_name: document.getElementById('last-name').value,
        address: document.getElementById('address').value,
        state: document.getElementById('state').value,
        zip: document.getElementById('zip').value
    };
    closeModal('personalModal');
    alert("Personal information saved!");
}


document.addEventListener('DOMContentLoaded', function() {
    // Initialize Stripe with your publishable key
    stripe = Stripe("pk_test_51RFkha4CIKoglRouRwgnFxHzUaW7vWCRELLnWAT5wVXo4dQiXWHHvLqdM7T7Fb2CIsML2HniahWELmmpwCZc1Ufh00yTgzbljc"); // Replace with your actual publishable key
});


function initializeStripeElements() {
    // Get the total amount from the page
    const totalElement = document.querySelector('.total-amount');
    const totalText = totalElement ? totalElement.textContent : '';
    const totalMatch = totalText.match(/\$(\d+\.\d+)/);
    const total = totalMatch ? parseFloat(totalMatch[1]) * 100 : 0; // Convert to cents


    fetch("/create-payment-intent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ amount: Math.round(total) })
    })
    .then(res => res.json())
    .then(data => {
        clientSecret = data.clientSecret;

        elements = stripe.elements({
            clientSecret: clientSecret,
            appearance: {
                theme: 'stripe',
                variables: {
                    colorPrimary: '#2e7d32',
                    colorText: '#000000',
                    colorTextSecondary: '#000000',
                    colorTextPlaceholder: '#000000',
                    colorBackground: 'rgba(255, 255, 255, 0.95)',
                    fontFamily: 'Arial, sans-serif',
                },
                rules: {
                    '.Label': {
                        color: '#000000',
                        fontWeight: 'bold'
                    },
                    '.Tab': {
                        color: '#000000',
                        borderColor: '#2e7d32'
                    },
                    '.Tab:hover': {
                        color: '#2e7d32'
                    },
                    '.Tab--selected': {
                        borderColor: '#2e7d32',
                        color: '#2e7d32'
                    },
                    '.Input': {
                        backgroundColor: '#ffffff',
                        borderColor: '#cccccc'
                    },
                    '.Input:focus': {
                        borderColor: '#2e7d32'
                    },
                    '.CheckboxInput': {
                        backgroundColor: '#ffffff',
                        borderColor: '#cccccc'
                    },
                    '.CheckboxInput--checked': {
                        backgroundColor: '#2e7d32'
                    }
                }
            }
        });


        paymentElement = elements.create('payment');
        paymentElement.mount('#payment-element');
    })
    .catch(error => {
        console.error('Error creating payment intent:', error);
        document.getElementById('payment-error').textContent = 'Failed to initialize payment system. Please try again.';
        document.getElementById('payment-error').style.display = 'block';
    });
}

const originalOpenModal = openModal;
openModal = function(id) {
    originalOpenModal(id);
    if (id === 'paymentModal') {
        initializeStripeElements();
    }
};

// Handle payment submission
async function handlePaymentSubmission() {
    const ccFirstName = document.getElementById("cc-first-name").value.trim();
    const ccLastName = document.getElementById("cc-last-name").value.trim();
    const ccAddress = document.getElementById("cc-address").value.trim();

    if (!ccFirstName || !ccLastName || !ccAddress) {
        alert("Please fill in all billing information fields.");
        return;
    }

    // Show loading state
    const submitButton = document.getElementById("submit-payment");
    submitButton.disabled = true;
    submitButton.textContent = "Processing...";

    try {
        // Confirm the payment with Stripe
        const { error, paymentIntent } = await stripe.confirmPayment({
            elements,
            confirmParams: {
                return_url: window.location.origin + "/checkout",
                payment_method_data: {
                    billing_details: {
                        name: `${ccFirstName} ${ccLastName}`,
                        address: {
                            line1: ccAddress
                        }
                    }
                }
            },
            redirect: 'if_required'
        });

        if (error) {
            // Stripe already shows its own error messages in the UI
            submitButton.disabled = false;
            submitButton.textContent = "Confirm Payment";
        } else if (paymentIntent && paymentIntent.status === 'succeeded') {
            // Payment succeeded, store payment info and close modal
            paymentInfo = {
                cc_first_name: ccFirstName,
                cc_last_name: ccLastName,
                cc_address: ccAddress,
                payment_intent_id: paymentIntent.id,
                payment_method: paymentIntent.payment_method,
                payment_status: paymentIntent.status
            };

            alert("Payment processed successfully!");
            closeModal("paymentModal");
        }
    } catch (e) {
        console.error('Payment error:', e);
        // Only show our error message for unexpected errors not handled by Stripe
        document.getElementById('payment-error').textContent = 'An unexpected error occurred. Please try again.';
        document.getElementById('payment-error').style.display = 'block';
        submitButton.disabled = false;
        submitButton.textContent = "Confirm Payment";
    }
}


function confirmOrder() {
    // Check if all personal info fields are filled
    const personalFieldsFilled = personalInfo.first_name && personalInfo.last_name &&
                                personalInfo.address && personalInfo.state && personalInfo.zip;

    // Check if payment info is filled (now includes Stripe payment details)
    const paymentFieldsFilled = paymentInfo.cc_first_name && paymentInfo.cc_last_name &&
                                paymentInfo.cc_address && paymentInfo.payment_intent_id &&
                                paymentInfo.payment_status === 'succeeded';

    if (!personalFieldsFilled || !paymentFieldsFilled) {
        alert("Please complete both personal and payment information before confirming your order.");
        return;
    }

    // Show loading state on the confirm order button
    const confirmBtn = document.querySelector(".confirm-order-btn");
    if (confirmBtn) {
        confirmBtn.disabled = true;
        confirmBtn.textContent = "Processing...";
    }

    fetch("/place_order", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            personal: personalInfo,
            payment: paymentInfo
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.orderNumber) {
            document.getElementById("order-number").innerText = data.orderNumber;
            document.getElementById("order-success").style.display = "block";

            if (confirmBtn) {
                confirmBtn.disabled = true;
                confirmBtn.style.opacity = "0.6";
                confirmBtn.innerText = "Order Submitted";
            }

            // Disable personal/payment buttons
            document.querySelectorAll(".show-form-btn").forEach(btn => btn.style.display = "none");

            // Disable quantity and remove buttons
            document.querySelectorAll(".decrease, .increase, .remove-item").forEach(btn => {
                btn.disabled = true;
                btn.style.opacity = "0.6";
                btn.style.cursor = "not-allowed";
            });

        } else {
            alert("Error placing order: " + (data.error || "Unknown error"));
            if (confirmBtn) {
                confirmBtn.disabled = false;
                confirmBtn.textContent = "Confirm Order";
            }
        }
    })
    .catch(err => {
        console.error("Error:", err);
        alert("Something went wrong!");
        if (confirmBtn) {
            confirmBtn.disabled = false;
            confirmBtn.textContent = "Confirm Order";
        }
    });
}

// Name validation script for NomNom Bites
// Prevents numbers and special characters in name fields

/**
 * Validates a name field to ensure it contains only letters, spaces, hyphens, and apostrophes
 * @param {HTMLInputElement} inputElement - The input element to validate
 * @returns {boolean} - True if valid, false if invalid
 */
function validateNameField(inputElement) {
  // Regular expression to match only letters, spaces, hyphens, and apostrophes
  const nameRegex = /^[A-Za-z\s\-']+$/;
  
  // Get the current value of the input
  const value = inputElement.value;
  
  // Check if the value matches the regex
  const isValid = nameRegex.test(value);
  
  // If invalid, show error styling and return false
  if (!isValid && value !== '') {
    inputElement.setCustomValidity("Please enter a valid name (letters, spaces and hyphens only)");
    inputElement.style.borderColor = 'red';
    return false;
  } else {
    // If valid, clear any error styling and return true
    inputElement.setCustomValidity("");
    inputElement.style.borderColor = '';
    return true;
  }
}

/**
 * Attaches validation to name input fields
 * @param {string} nameInputSelector - CSS selector for the name input field
 * @param {string} lastNameInputSelector - CSS selector for the last name input field
 */
function setupNameValidation(nameInputSelector, lastNameInputSelector) {
  // Get the input elements
  const nameInput = document.querySelector(nameInputSelector);
  const lastNameInput = document.querySelector(lastNameInputSelector);
  
  // Add validation to the name input
  if (nameInput) {
    nameInput.addEventListener('input', function() {
      validateNameField(this);
    });
    
    nameInput.addEventListener('blur', function() {
      validateNameField(this);
    });
  }
  
  // Add validation to the last name input
  if (lastNameInput) {
    lastNameInput.addEventListener('input', function() {
      validateNameField(this);
    });
    
    lastNameInput.addEventListener('blur', function() {
      validateNameField(this);
    });
  }
}
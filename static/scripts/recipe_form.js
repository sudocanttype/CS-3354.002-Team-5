document.addEventListener('DOMContentLoaded', function() {
  const addIngredientBtn = document.querySelector('.add-ingredient');
  if (addIngredientBtn) {
    addIngredientBtn.addEventListener('click', function() {
      const ingredientItem = document.createElement('div');
      ingredientItem.className = 'ingredient-item';

      alert('Add ingredient functionality will be implemented later');
    });
  }

  const addStepBtn = document.querySelector('.add-step');
  if (addStepBtn) {
    addStepBtn.addEventListener('click', function() {
      alert('Add step functionality will be implemented later');
    });
  }

  const addTagBtn = document.querySelector('.tag-add');
  if (addTagBtn) {
    addTagBtn.addEventListener('click', function() {
      alert('Add tag functionality will be implemented later');
    });
  }

  const imageUploadBtn = document.querySelector('.image-upload-btn');
  if (imageUploadBtn) {
    imageUploadBtn.addEventListener('click', function() {
      alert('Image upload functionality will be implemented later');
    });
  }

  const cancelBtn = document.querySelector('.btn-secondary');
  if (cancelBtn) {
    cancelBtn.addEventListener('click', function() {
      window.location.href = '/recipes';
    });
  }
}); 
document.addEventListener('DOMContentLoaded', function() {
  const addRecipeBtn = document.querySelector('.add-recipe');
  if (addRecipeBtn) {
    addRecipeBtn.addEventListener('mouseenter', function() {
      this.querySelector('.add-recipe-text').style.color = '#E6A800';
    });
    
    addRecipeBtn.addEventListener('mouseleave', function() {
      this.querySelector('.add-recipe-text').style.color = '';
    });
  }

  const recipeCards = document.querySelectorAll('.recipe-card');
  recipeCards.forEach(card => {
    card.addEventListener('click', function() {
      this.style.transform = 'scale(0.98)';
      setTimeout(() => {
        this.style.transform = '';
      }, 100);
    });
  });
}); 
function favoriteRecipe(recipeId) {
  fetch('/favorite', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      username: currentUsername,
      recipeId: recipeId
    })
  })
  .then(res => res.json())
  .then(data => alert(data.message))
  .catch(err => console.error('Failed to favorite recipe:', err));
}

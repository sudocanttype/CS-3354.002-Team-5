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
  .then(data => {
    if (data.message) {
      alert(data.message);  // ✅ success
    } else if (data.error) {
      alert("Error: " + data.error);  // ❌ shows error clearly
    } else {
      alert("Unexpected response");
    }
  })
  .catch(err => {
    console.error('Favorite failed:', err);
    alert("Request failed");
  });
}

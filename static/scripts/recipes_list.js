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

  const recipeFilter = document.getElementById('recipe-filter');

  // Avoid multiple event listeners being added
  if (!recipeFilter || recipeFilter.dataset.listenerAttached === 'true') return;

  console.log("Favorite IDs:", favoriteIDs);

  recipeFilter.addEventListener('change', function () {
    const filterValue = this.value;
    const recipes = document.querySelectorAll('.recipe-box');

    console.log("Filter changed to:", filterValue);

    recipes.forEach(recipe => {
      const recipeId = String(recipe.getAttribute('data-id'));
      const isFavorite = favoriteIDs.includes(recipeId);
      console.log(`Recipe ID ${recipeId} - isFavorite: ${isFavorite}`);

      if (filterValue === 'favorites' && !isFavorite) {
        recipe.style.display = 'none';
      } else {
        recipe.style.display = 'block';
      }
    });
  });

  // Mark listener as attached so it doesn't get added again
  recipeFilter.dataset.listenerAttached = 'true';
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
      alert(data.message);
      favoriteIDs.push(String(recipeId));  // ✅ Add it to the list manually
      // Optional: visually toggle heart icon here
    } else {
      alert("Error: " + data.error);
    }
  })
  .catch(err => {
    console.error('Favorite toggle failed:', err);
    alert("Something went wrong");
  });
}

window.favoriteRecipe = favoriteRecipe;

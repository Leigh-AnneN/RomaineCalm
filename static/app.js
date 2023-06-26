
// Function to handle deleting a garden
function deleteGarden(gardenId) {
    if(confirm('Are you sure you want to delete this garden?')) {
        //send an AJAX request to delete a garden
   fetch(`/gardens/${gardenId}`, {
            method: 'DELETE',
          })
          .then(response => {
            if (response.ok) {
              // Handle successful deletion
              console.log("Garden deleted successfully");
              location.reload();
            } else {
              // Handle deletion failure
              console.error("Failed to delete garden");
            }
          })
          .catch(error => {
            // Handle error if any
            console.error(error);
          });
        }
    }

// Function to handle deleting a plant
function deletePlant(gardenId, plantId) {
    if (confirm('Are you sure you want to delete this plant?')) {
      fetch(`/gardens/${gardenId}/plants/${plantId}`, {
        method: 'DELETE',
      })
      .then(response => {
        if (response.ok) {
          // Handle successful deletion
          console.log("Plant deleted successfully");
          location.reload();
        } else {
          // Handle deletion failure
          console.error("Failed to delete plant");
        }
      })
      .catch(error => {
        // Handle error if any
        console.error(error);
      });
    }
  }

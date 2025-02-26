document.getElementById('recommendForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const input = document.getElementById('songsInput').value;
    const songsArray = input.split(',').map(song => song.trim()).filter(song => song !== "");
    
    fetch('/api/recommend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ songs: songsArray })
    })
    .then(response => {
      if (!response.ok) {
        return response.json().then(err => { throw err; });
      }
      return response.json();
    })
    .then(data => {
      let html = `<h3>Recommendations:</h3>`;
      // Check if the API provided a message (i.e. no direct recommendation via rules)
      if (data.songs && data.songs.length > 0) {
        if (data.message) {
          html += `<p class="text-info">No direct recommendations found. Here are 3 random recommendations:</p>`;
        }
        html += `<ul>`;
        data.songs.forEach(song => {
          html += `<li>${song}</li>`;
        });
        html += `</ul>`;
      } else if(data.error) {
        html += `<p class="text-danger">${data.error}</p>`;
      } else {
        html += `<p>No recommendations found.</p>`;
      }
      html += `<p><strong>Version:</strong> ${data.version}</p>`;
      html += `<p><strong>Model Date:</strong> ${data.model_date}</p>`;
      document.getElementById('results').innerHTML = html;
    })
    .catch(error => {
      console.error('Error:', error);
      document.getElementById('results').innerHTML = `<p class="text-danger">Error: ${error.error || 'An unexpected error occurred.'}</p>`;
    });
  });
  
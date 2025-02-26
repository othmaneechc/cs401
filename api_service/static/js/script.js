// Global array to store added songs
let addedSongs = [];

// Update the displayed list of user-added songs
function updateSongList() {
  const songList = document.getElementById('songList');
  songList.innerHTML = '';
  addedSongs.forEach((song, index) => {
    const li = document.createElement('li');
    li.textContent = song;
    songList.appendChild(li);
  });
}

// Event listener for adding a song
document.getElementById('addSongBtn').addEventListener('click', function() {
  const songInput = document.getElementById('songInput');
  const song = songInput.value.trim();
  if (song) {
    addedSongs.push(song);
    updateSongList();
    songInput.value = '';
  }
});

// Event listener for resetting the list
document.getElementById('resetSongsBtn').addEventListener('click', function() {
  addedSongs = [];
  updateSongList();
  document.getElementById('results').innerHTML = '';
});

// Event listener for getting recommendations
document.getElementById('getRecBtn').addEventListener('click', function() {
  if (addedSongs.length === 0) {
    alert("Please add at least one song.");
    return;
  }
  
  fetch('/api/recommend', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ songs: addedSongs })
  })
  .then(response => {
    if (!response.ok) {
      return response.json().then(err => { throw err; });
    }
    return response.json();
  })
  .then(data => {
    let html = `<h3>Your Songs:</h3>`;
    html += `<ul>`;
    addedSongs.forEach(song => {
      html += `<li>${song}</li>`;
    });
    html += `</ul>`;
    
    html += `<h3>Recommendations:</h3>`;
    if (data.songs && data.songs.length > 0) {
      if (data.message) {
        html += `<p class="text-info">${data.message}</p>`;
      }
      html += `<ul>`;
      data.songs.forEach(song => {
        // URL-encode the song name for the SoundCloud link.
        const soundcloudLink = "https://soundcloud.com/search?q=" + encodeURIComponent(song);
        html += `<li class="recommendation-item">
                  <span>${song}</span>
                  <a href="${soundcloudLink}" target="_blank">
                    <button class="play-btn">▶</button>
                  </a>
                </li>`;
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

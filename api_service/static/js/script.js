// Global array to store added songs
let addedSongs = [];

// Update the displayed list of user-added songs with a SoundCloud link for each
function updateSongList() {
  const songList = document.getElementById('songList');
  songList.innerHTML = '';
  addedSongs.forEach((song, index) => {
    // Create a SoundCloud search URL for this song.
    const soundcloudLink = "https://soundcloud.com/search?q=" + encodeURIComponent(song);
    
    const li = document.createElement('li');
    li.classList.add('song-item');
    
    // Create a span to hold the song text
    const songText = document.createElement('span');
    songText.textContent = song;
    
    // Create a link wrapping the play button
    const link = document.createElement('a');
    link.href = soundcloudLink;
    link.target = "_blank";
    
    const playBtn = document.createElement('button');
    playBtn.classList.add('play-btn');
    playBtn.textContent = '▶';  // Play button icon
    
    link.appendChild(playBtn);
    
    li.appendChild(songText);
    li.appendChild(link);
    
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
      // Create SoundCloud search link for the added song.
      const soundcloudLink = "https://soundcloud.com/search?q=" + encodeURIComponent(song);
      html += `<li class="recommendation-item">
                <span>${song}</span>
                <a href="${soundcloudLink}" target="_blank">
                  <button class="play-btn">▶</button>
                </a>
              </li>`;
    });
    html += `</ul>`;
    
    html += `<h3>Recommendations:</h3>`;
    if (data.songs && data.songs.length > 0) {
      if (data.message) {
        html += `<p class="text-info">${data.message}</p>`;
      }
      html += `<ul>`;
      data.songs.forEach(song => {
        // Create a SoundCloud link for each recommended song.
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

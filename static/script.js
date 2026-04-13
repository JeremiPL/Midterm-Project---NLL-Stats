// NLL Box Lacrosse Stats App - Frontend
const API_BASE = '/api';

// DOM Elements
const playerGrid = document.getElementById('playerGrid');
const loadingSpinner = document.getElementById('loadingSpinner');
const emptyState = document.getElementById('emptyState');
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const resetBtn = document.getElementById('resetBtn');
const playerModal = document.getElementById('playerModal');
const closeBtn = document.querySelector('.close');
const playerCount = document.getElementById('playerCount');
const filterButtons = document.querySelectorAll('.filter-btn');

// State
let allPlayers = [];
let filteredPlayers = [];
let activeFilter = 'all';

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    loadPlayers();
    attachEventListeners();
});

// Event Listeners
function attachEventListeners() {
    searchBtn.addEventListener('click', performSearch);
    resetBtn.addEventListener('click', resetFilters);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') performSearch();
    });
    closeBtn.addEventListener('click', closeModal);
    window.addEventListener('click', (e) => {
        if (e.target === playerModal) closeModal();
    });

    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => handleFilterClick(btn));
    });
}

// Load all players from API
async function loadPlayers() {
    try {
        loadingSpinner.style.display = 'block';
        playerGrid.innerHTML = '';
        emptyState.style.display = 'none';

        const response = await fetch(`${API_BASE}/players`);
        if (!response.ok) throw new Error('Failed to load players');

        allPlayers = await response.json();
        filteredPlayers = [...allPlayers];

        if (allPlayers.length === 0) {
            showEmptyState();
        } else {
            displayPlayers(filteredPlayers);
        }
    } catch (error) {
        console.error('Error loading players:', error);
        showErrorMessage('Failed to load player data. Please try again.');
    } finally {
        loadingSpinner.style.display = 'none';
    }
}

// Display players in grid
function displayPlayers(players) {
    playerGrid.innerHTML = '';
    playerCount.textContent = players.length;

    if (players.length === 0) {
        showEmptyState();
        return;
    }

    emptyState.style.display = 'none';

    players.forEach(player => {
        const card = createPlayerCard(player);
        playerGrid.appendChild(card);
    });
}

// Create player card element
function createPlayerCard(player) {
    const card = document.createElement('div');
    card.className = 'player-card';

    const goalsEarned = player.goals || 0;
    const assistsEarned = player.assists || 0;
    const pointsTotal = player.points || 0;

    card.innerHTML = `
        <div class="player-header">
            <div class="player-name">${escapeHtml(player.player_name || 'Unknown')}</div>
            <span class="player-position">${escapeHtml(getPositionLabel(player.position))}</span>
            <div class="player-team">${escapeHtml(player.team || 'N/A')}</div>
        </div>
        <div class="player-stats">
            <div class="stat-item">
                <div class="stat-label">Goals</div>
                <div class="stat-value">${goalsEarned}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Assists</div>
                <div class="stat-value">${assistsEarned}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Points</div>
                <div class="stat-value">${pointsTotal}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">GP</div>
                <div class="stat-value">${player.games_played || 0}</div>
            </div>
        </div>
        <button class="view-details-btn" onclick="viewPlayerDetails(${player.player_id})">
            View Details
        </button>
    `;

    return card;
}

// View player details modal
async function viewPlayerDetails(playerId) {
    try {
        const response = await fetch(`${API_BASE}/players/${playerId}`);
        if (!response.ok) throw new Error('Failed to load player details');

        const playerData = await response.json();

        if (playerData.error) {
            showErrorMessage(playerData.error);
            return;
        }

        const modalBody = document.getElementById('modalBody');
        modalBody.innerHTML = createModalContent(playerData);
        playerModal.classList.add('show');
    } catch (error) {
        console.error('Error loading player details:', error);
        showErrorMessage('Failed to load player details.');
    }
}

// Create modal content
function createModalContent(playerData) {
    const profile = playerData.profile || {};
    const stats = playerData.stats || {};

    if (!stats.games_played) {
        return `
            <div class="modal-header">
                <div class="modal-player-info">
                    <h2>${escapeHtml(profile.player_name || 'Unknown')}</h2>
                    ${profile.position ? `<span class="modal-position">${escapeHtml(profile.position)}</span>` : ''}
                    ${profile.team ? `<span class="modal-team">${escapeHtml(profile.team)}</span>` : ''}
                </div>
            </div>
            <div class="bio-section">
                <div class="section-title">Personal Information</div>
                <p style="color: var(--text-light); text-align: center;">No data available for this player.</p>
            </div>
        `;
    }

    return `
        <div class="modal-header">
            <div class="modal-player-info">
                <h2>${escapeHtml(profile.player_name || 'Unknown')}</h2>
                ${profile.position ? `<span class="modal-position">${escapeHtml(getPositionLabel(profile.position))}</span>` : ''}
                ${profile.team ? `<span class="modal-team">${escapeHtml(profile.team)}</span>` : ''}
            </div>
        </div>

        ${profile.number || profile.age || profile.hometown || profile.birthdate || profile.height || profile.weight ? `
            <div class="bio-section">
                <div class="section-title">Personal Information</div>
                <div class="bio-grid">
                    ${profile.number ? `
                        <div class="bio-item">
                            <div class="bio-label">Number</div>
                            <div class="bio-value">#${profile.number}</div>
                        </div>
                    ` : ''}
                    ${profile.age ? `
                        <div class="bio-item">
                            <div class="bio-label">Age</div>
                            <div class="bio-value">${profile.age}</div>
                        </div>
                    ` : ''}
                    ${profile.height ? `
                        <div class="bio-item">
                            <div class="bio-label">Height</div>
                            <div class="bio-value">${escapeHtml(profile.height)}</div>
                        </div>
                    ` : ''}
                    ${profile.weight ? `
                        <div class="bio-item">
                            <div class="bio-label">Weight</div>
                            <div class="bio-value">${escapeHtml(profile.weight)}</div>
                        </div>
                    ` : ''}
                    ${profile.shoots ? `
                        <div class="bio-item">
                            <div class="bio-label">Shoots</div>
                            <div class="bio-value">${escapeHtml(profile.shoots)}</div>
                        </div>
                    ` : ''}
                    ${profile.hometown ? `
                        <div class="bio-item">
                            <div class="bio-label">Hometown</div>
                            <div class="bio-value">${escapeHtml(profile.hometown)}</div>
                        </div>
                    ` : ''}
                    ${profile.birthdate ? `
                        <div class="bio-item">
                            <div class="bio-label">DOB</div>
                            <div class="bio-value">${escapeHtml(profile.birthdate)}</div>
                        </div>
                    ` : ''}
                    ${profile.college ? `
                        <div class="bio-item">
                            <div class="bio-label">College</div>
                            <div class="bio-value">${escapeHtml(profile.college)}</div>
                        </div>
                    ` : ''}
                </div>
            </div>
        ` : ''}

        <div class="stats-section-detail">
            <div class="section-title">Career Statistics</div>
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="stat-box-label">Games Played</div>
                    <div class="stat-box-value">${stats.games_played || 0}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-box-label">Goals</div>
                    <div class="stat-box-value">${stats.goals || 0}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-box-label">Assists</div>
                    <div class="stat-box-value">${stats.assists || 0}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-box-label">Points</div>
                    <div class="stat-box-value">${stats.points || 0}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-box-label">Shots on Goal</div>
                    <div class="stat-box-value">${stats.shots_on_goal || 0}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-box-label">Loose Balls</div>
                    <div class="stat-box-value">${stats.loose_balls || 0}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-box-label">Turnovers</div>
                    <div class="stat-box-value">${stats.turnovers || 0}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-box-label">Penalty Min</div>
                    <div class="stat-box-value">${stats.penalty_minutes || 0}</div>
                </div>
                ${stats.faceoffs_won !== null ? `
                    <div class="stat-box">
                        <div class="stat-box-label">Faceoffs Won</div>
                        <div class="stat-box-value">${stats.faceoffs_won || 0}</div>
                    </div>
                ` : ''}
                ${stats.faceoff_percentage !== null ? `
                    <div class="stat-box">
                        <div class="stat-box-label">Faceoff %</div>
                        <div class="stat-box-value">${stats.faceoff_percentage ? stats.faceoff_percentage.toFixed(1) : 'N/A'}%</div>
                    </div>
                ` : ''}
                ${stats.caused_turnovers !== null ? `
                    <div class="stat-box">
                        <div class="stat-box-label">Caused TOs</div>
                        <div class="stat-box-value">${stats.caused_turnovers || 0}</div>
                    </div>
                ` : ''}
                ${stats.minutes_played !== null ? `
                    <div class="stat-box">
                        <div class="stat-box-label">Minutes Played</div>
                        <div class="stat-box-value">${stats.minutes_played}</div>
                    </div>
                ` : ''}
                ${stats.saves !== null ? `
                    <div class="stat-box">
                        <div class="stat-box-label">Saves</div>
                        <div class="stat-box-value">${stats.saves || 0}</div>
                    </div>
                ` : ''}
                ${stats.goals_against !== null ? `
                    <div class="stat-box">
                        <div class="stat-box-label">Goals Against</div>
                        <div class="stat-box-value">${stats.goals_against || 0}</div>
                    </div>
                ` : ''}
                ${stats.goals_against_average !== null ? `
                    <div class="stat-box">
                        <div class="stat-box-label">GAA</div>
                        <div class="stat-box-value">${stats.goals_against_average ? stats.goals_against_average.toFixed(2) : 'N/A'}</div>
                    </div>
                ` : ''}
                ${stats.save_percentage !== null ? `
                    <div class="stat-box">
                        <div class="stat-box-label">Save %</div>
                        <div class="stat-box-value">${stats.save_percentage ? stats.save_percentage.toFixed(1) : 'N/A'}%</div>
                    </div>
                ` : ''}
                ${stats.wins !== null ? `
                    <div class="stat-box">
                        <div class="stat-box-label">Wins</div>
                        <div class="stat-box-value">${stats.wins || 0}</div>
                    </div>
                ` : ''}
                ${stats.losses !== null ? `
                    <div class="stat-box">
                        <div class="stat-box-label">Losses</div>
                        <div class="stat-box-value">${stats.losses || 0}</div>
                    </div>
                ` : ''}
            </div>
        </div>
    `;
}

// Search functionality
function performSearch() {
    const query = searchInput.value.toLowerCase().trim();

    if (!query) {
        filteredPlayers = [...allPlayers];
    } else {
        filteredPlayers = allPlayers.filter(player => {
            return (
                (player.player_name && player.player_name.toLowerCase().includes(query)) ||
                (player.team && player.team.toLowerCase().includes(query)) ||
                (player.position && player.position.toLowerCase().includes(query))
            );
        });
    }

    activeFilter = 'all';
    filterButtons.forEach(btn => btn.classList.remove('active'));
    filterButtons[0].classList.add('active');

    displayPlayers(filteredPlayers);
}

// Handle filter clicks
function handleFilterClick(btn) {
    filterButtons.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    const filterType = btn.dataset.filter;

    if (filterType === 'all') {
        filteredPlayers = [...allPlayers];
    } else {
        const positionKey = filterType.replace('position-', '').toUpperCase();
        filteredPlayers = allPlayers.filter(player => {
            return player.position && player.position.toUpperCase().includes(positionKey);
        });
    }

    activeFilter = filterType;
    searchInput.value = '';
    displayPlayers(filteredPlayers);
}

// Reset filters
function resetFilters() {
    searchInput.value = '';
    activeFilter = 'all';
    filteredPlayers = [...allPlayers];
    filterButtons.forEach(b => b.classList.remove('active'));
    filterButtons[0].classList.add('active');
    displayPlayers(filteredPlayers);
}

// Close modal
function closeModal() {
    playerModal.classList.remove('show');
    document.getElementById('modalBody').innerHTML = '';
}

// Show empty state
function showEmptyState() {
    playerGrid.innerHTML = '';
    emptyState.style.display = 'block';
    playerCount.textContent = '0';
}

// Show error message
function showErrorMessage(message) {
    playerGrid.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 2rem; color: var(--danger-color);">
            <p>${escapeHtml(message)}</p>
        </div>
    `;
}

// Helper: Get position label
function getPositionLabel(position) {
    if (!position) return 'Unknown';
    const positionMap = {
        'FORWARD': 'Forward',
        'TRANSITION': 'Transition',
        'DEFENCE': 'Defence',
        'GOALTENDER': 'Goaltender',
    };
    return positionMap[position.toUpperCase()] || position;
}

// Helper: Escape HTML
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// NLL Box Lacrosse Stats App - Frontend
const API_BASE = '/api';

// DOM Elements
const playerGrid = document.getElementById('playerGrid');
const loadingSpinner = document.getElementById('loadingSpinner');
const emptyState = document.getElementById('emptyState');
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const resetBtn = document.getElementById('resetBtn');
const teamFilter = document.getElementById('teamFilter');
const seasonFilter = document.getElementById('seasonFilter');
const positionFilter = document.getElementById('positionFilter');
const playerModal = document.getElementById('playerModal');
const closeBtn = document.querySelector('.close');
const playerCount = document.getElementById('playerCount');
const tabButtons = document.querySelectorAll('.tab-btn');
const appPages = document.querySelectorAll('.app-page');
const scheduleSeasonFilter = document.getElementById('scheduleSeasonFilter');
const scheduleStageFilter = document.getElementById('scheduleStageFilter');
const scheduleWeekFilter = document.getElementById('scheduleWeekFilter');
const scheduleTeamFilter = document.getElementById('scheduleTeamFilter');
const scheduleRefreshBtn = document.getElementById('scheduleRefreshBtn');
const scheduleTableBody = document.getElementById('scheduleTableBody');
const scheduleLoading = document.getElementById('scheduleLoading');
const standingSeasonFilter = document.getElementById('standingSeasonFilter');
const standingStageFilter = document.getElementById('standingStageFilter');
const standingsRefreshBtn = document.getElementById('standingsRefreshBtn');
const standingsTableBody = document.getElementById('standingsTableBody');
const standingsCards = document.getElementById('standingsCards');
const standingsLoading = document.getElementById('standingsLoading');
const standingsCount = document.getElementById('standingsCount');
const playoffBracket = document.getElementById('playoffBracket');
const playoffBracketGrid = document.getElementById('playoffBracketGrid');

// State
let allPlayers = [];
let filteredPlayers = [];
let scheduleLoaded = false;
let standingsLoaded = false;

// Team palettes: primary, secondary, accent and optional neutrals.
const TEAM_COLOR_SCHEMES = {
    'oshawa firewolves': ['#7A303F', '#D0B787', '#FFFFFF', '#000000'],
    'buffalo bandits': ['#F58521', '#302C93', '#FFFFFF', '#A8AAAD', '#000000'],
    'san diego seals': ['#000000', '#623295', '#B4B2B3', '#FBB426'],
    'colorado mammoth': ['#98002E', '#B0B6BB', '#FFFFFF', '#000000'],
    'georgia swarm': ['#FCB000', '#00204D', '#FFFFFF', '#A9ACAD'],
    'vancouver warriors': ['#000000', '#B3A067', '#C2C2C2', '#FFFFFF'],
    'calgary roughnecks': ['#C8102E', '#010101', '#A6BBC8'],
    'toronto rock': ['#EF3E33', '#005A9C', '#FFCB05', '#CACCCE', '#FFFFFF', '#000000'],
    'saskatchewan rush': ['#81C341', '#000000', '#FFFFFF'],
    'las vegas desert dogs': ['#FFFFFF', '#000000'],
    'philadelphia wings': ['#F8DC8D', '#FE0000', '#7B7C80', '#3F3F40'],
    'halifax thunderbirds': ['#592D8B', '#F15922', '#401564', '#B34215'],
    'rochester knighthawks': ['#4E5B31', '#010101', '#BD9B60', '#D0D0CE'],
    'ottawa black bears': ['#DA1A32', '#000000', '#B79257', '#FFFFFF'],

    // Alias to handle common alternate naming.
    'albany firewolves': ['#7A303F', '#D0B787', '#FFFFFF', '#000000'],
};

const TEAM_ALIASES = {
    buffalo: 'buffalo bandits',
    sandiego: 'san diego seals',
    colorado: 'colorado mammoth',
    georgia: 'georgia swarm',
    vancouver: 'vancouver warriors',
    calgary: 'calgary roughnecks',
    toronto: 'toronto rock',
    saskatchewan: 'saskatchewan rush',
    lasvegas: 'las vegas desert dogs',
    philadelphia: 'philadelphia wings',
    halifax: 'halifax thunderbirds',
    rochester: 'rochester knighthawks',
    ottawa: 'ottawa black bears',
    oshawa: 'oshawa firewolves',
    albany: 'albany firewolves'
};

const TEAM_LOGOS = {
    'oshawa firewolves': 'Oshawa_FireWolves Logo.png',
    'buffalo bandits': 'Buffalo_Bandits_logo.svg.png',
    'san diego seals': 'San_Diego_Seals_primary_logo.png',
    'colorado mammoth': 'Colorado mammoth logo.svg',
    'georgia swarm': 'Georgia Swarm Logo.webp',
    'vancouver warriors': 'Vancouver_Warriors_Logo.png',
    'calgary roughnecks': 'Calgary_Roughnecks_logo.svg.png',
    'toronto rock': 'Toronto_Rock_logo.svg.png',
    'saskatchewan rush': 'Saskatchewan_Rush_logo.png',
    'las vegas desert dogs': 'Las_Vegas_Desert_Dogs logo.png',
    'philadelphia wings': 'Philadelphia_Wings logo.png',
    'halifax thunderbirds': 'Halifax_Thunderbirds_logo.png',
    'rochester knighthawks': 'Rochester_Knighthawks_logo.png',
    'ottawa black bears': 'Ottawa Black Bears logo.png',
    'albany firewolves': 'Oshawa_FireWolves Logo.png'
};

const DEFAULT_TEAM_LOGO = 'team-logos/default-logo.svg';

const PLAYOFF_2026_QUARTERFINAL_RESULTS = {
    'Vancouver Warriors|Halifax Thunderbirds': { highScore: 7, lowScore: 10, winner: 'low' },
    'Colorado Mammoth|San Diego Seals': { highScore: 12, lowScore: 13, winner: 'low' },
    'Saskatchewan Rush|Toronto Rock': { highScore: 13, lowScore: 16, winner: 'low' },
    'Georgia Swarm|Buffalo Bandits': { highScore: 17, lowScore: 10, winner: 'high' },
};

const PLAYOFF_2026_STANDINGS_ORDER = [
    'Georgia Swarm',
    'Toronto Rock',
    'San Diego Seals',
    'Halifax Thunderbirds',
    'Vancouver Warriors',
    'Colorado Mammoth',
    'Saskatchewan Rush',
    'Buffalo Bandits',
];

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    loadPlayers();
    attachEventListeners();
});

const POSITION_SORT_METRICS = {
    DEFENCE: 'caused_turnovers',
    GOALTENDER: 'wins',
};

// Event Listeners
function attachEventListeners() {
    searchBtn.addEventListener('click', performSearch);
    resetBtn.addEventListener('click', resetFilters);
    teamFilter.addEventListener('change', applyFilters);
    seasonFilter.addEventListener('change', applyFilters);
    positionFilter.addEventListener('change', applyFilters);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') performSearch();
    });
    closeBtn.addEventListener('click', closeModal);
    window.addEventListener('click', (e) => {
        if (e.target === playerModal) closeModal();
    });
    window.addEventListener('hashchange', () => {
        activateTab(getTabFromHash(), false);
    });

    if (scheduleRefreshBtn) {
        scheduleRefreshBtn.addEventListener('click', loadSchedule);
    }

    if (standingsRefreshBtn) {
        standingsRefreshBtn.addEventListener('click', loadStandings);
    }

}

function initTabs() {
    tabButtons.forEach((button) => {
        button.addEventListener('click', () => {
            activateTab(button.dataset.tab || 'player-profile', true);
        });
    });

    activateTab(getTabFromHash(), false);
}

function getTabFromHash() {
    const hashValue = window.location.hash.replace('#', '').trim();
    const validTabs = ['player-profile', 'league-standing', 'schedule', 'advanced-statistics'];
    return validTabs.includes(hashValue) ? hashValue : 'player-profile';
}

function activateTab(tabName, updateHash) {
    tabButtons.forEach((button) => {
        button.classList.toggle('active', button.dataset.tab === tabName);
    });

    appPages.forEach((page) => {
        page.classList.toggle('active', page.dataset.page === tabName);
    });

    if (updateHash) {
        window.location.hash = tabName;
    }

    if (tabName === 'schedule' && !scheduleLoaded) {
        loadSchedule();
    }

    if (tabName === 'league-standing' && !standingsLoaded) {
        loadStandings();
    }
}

async function loadStandings() {
    if (!standingsTableBody || !standingsLoading || !standingsCards) return;

    const seasonId = standingSeasonFilter ? standingSeasonFilter.value : '225';
    const stage = standingStageFilter ? standingStageFilter.value : 'REG';

    try {
        standingsLoading.style.display = 'block';
        renderStandingsEmpty('Loading standings...');

        const params = new URLSearchParams({
            season_id: seasonId,
            stage,
        });

        const response = await fetch(`${API_BASE}/standings?${params.toString()}`);
        if (!response.ok) {
            throw new Error('Failed to load standings');
        }

        if (stage === 'PO') {
            try {
                const seedParams = new URLSearchParams({
                    season_id: seasonId,
                    stage: 'REG',
                });
                const seedResponse = await fetch(`${API_BASE}/standings?${seedParams.toString()}`);
                if (!seedResponse.ok) {
                    throw new Error('Failed to load regular season seeds');
                }
                const seedData = await seedResponse.json();
                const seedRows = Array.isArray(seedData.standings) ? seedData.standings : [];

                const playoffRows = buildPlayoffStandingsRows(seedRows, seasonId);
                renderStandingsRows(playoffRows);
                renderPlayoffBracket(seedRows.slice(0, 8), seasonId);
            } catch (seedError) {
                console.error('Error loading regular season seeds:', seedError);
                const data = await response.json();
                const rows = Array.isArray(data.standings) ? data.standings : [];
                renderStandingsRows(rows);
                renderPlayoffBracket(rows.slice(0, 8), seasonId);
            }
        } else if (playoffBracket && playoffBracketGrid) {
            const data = await response.json();
            const rows = Array.isArray(data.standings) ? data.standings : [];
            renderStandingsRows(rows);
            playoffBracket.style.display = 'none';
            playoffBracketGrid.innerHTML = '';
        }

        standingsLoaded = true;
    } catch (error) {
        console.error('Error loading standings:', error);
        renderStandingsEmpty('Unable to load standings right now.');
    } finally {
        standingsLoading.style.display = 'none';
    }
}

function buildPlayoffStandingsRows(seedRows, seasonId) {
    const rows = seedRows.map((team) => ({
        ...team,
        wins: 0,
        losses: 0,
        gamesPlayed: 0,
        record: '0-0',
    }));

    if (seasonId !== '225') {
        return rows;
    }

    const topEight = rows.slice(0, 8);
    if (topEight.length < 8) {
        return rows;
    }

    const pairings = [
        [topEight[0], topEight[7]],
        [topEight[1], topEight[6]],
        [topEight[2], topEight[5]],
        [topEight[3], topEight[4]],
    ];

    const winners = [];
    const losers = [];

    pairings.forEach((pair) => {
        const highSeed = pair[0];
        const lowSeed = pair[1];
        const key = `${highSeed.team || ''}|${lowSeed.team || ''}`;
        const result = PLAYOFF_2026_QUARTERFINAL_RESULTS[key];

        if (!result) {
            return;
        }

        const winner = result.winner === 'high' ? highSeed : lowSeed;
        const loser = result.winner === 'high' ? lowSeed : highSeed;

        winner.wins = 1;
        winner.losses = 0;
        winner.gamesPlayed = 1;
        winner.record = '1-0';

        loser.wins = 0;
        loser.losses = 1;
        loser.gamesPlayed = 1;
        loser.record = '0-1';

        winners.push(winner);
        losers.push(loser);
    });

    const playoffRowsByTeam = {};
    [...winners, ...losers].forEach((team) => {
        playoffRowsByTeam[team.team] = team;
    });

    const playoffOrdered = PLAYOFF_2026_STANDINGS_ORDER
        .map((teamName) => playoffRowsByTeam[teamName])
        .filter(Boolean);

    playoffOrdered.forEach((team, index) => {
        team.rank = index + 1;
    });

    return playoffOrdered;
}

function renderStandingsRows(rows) {
    if (!standingsTableBody || !standingsCards) return;

    if (!rows.length) {
        renderStandingsEmpty('No standings available for these filters.');
        return;
    }

    if (standingsCount) {
        standingsCount.textContent = `${rows.length} Teams`;
    }

    const tableRows = [];

    rows.forEach((team, index) => {
        const teamName = team.team || 'Unknown Team';
        const logoPath = team.logo || getTeamLogoPath(teamName);

        tableRows.push(`
            <tr>
                <td><span class="standings-rank-badge">${Number(team.rank || 0)}</span></td>
                <td>
                    <div class="standings-team-cell">
                        <span class="standings-team-logo-wrap">
                            <img
                                class="standings-team-logo"
                                src="${escapeHtml(logoPath)}"
                                alt="${escapeHtml(teamName)} logo"
                                loading="lazy"
                                onerror="this.src='${DEFAULT_TEAM_LOGO}'; this.onerror=null;"
                            >
                        </span>
                        <span class="standings-team-name">${escapeHtml(teamName)}</span>
                    </div>
                </td>
                <td><span class="standings-record">${escapeHtml(team.record || '0-0')}</span></td>
                <td>${Number(team.gamesPlayed || 0)}</td>
            </tr>
        `);

        if (index === 7) {
            tableRows.push(`
                <tr class="standings-cutoff-row">
                    <td colspan="4">
                        <div class="standings-cutoff-line">
                            <span class="playoff-cutoff-tag">Playoff Cutoff</span>
                        </div>
                    </td>
                </tr>
            `);
        }
    });

    standingsTableBody.innerHTML = tableRows.join('');

    const cardRows = [];

    rows.forEach((team, index) => {
        const teamName = team.team || 'Unknown Team';
        const logoPath = team.logo || getTeamLogoPath(teamName);

        cardRows.push(`
            <article class="standing-card">
                <div class="standing-card-top">
                    <div class="standing-rank">#${Number(team.rank || 0)}</div>
                    <img
                        class="standing-card-logo"
                        src="${escapeHtml(logoPath)}"
                        alt="${escapeHtml(teamName)} logo"
                        loading="lazy"
                        onerror="this.src='${DEFAULT_TEAM_LOGO}'; this.onerror=null;"
                    >
                </div>
                <div class="standing-team-name">${escapeHtml(teamName)}</div>
                <div class="standing-record-row">
                    <span>Record</span>
                    <strong>${escapeHtml(team.record || '0-0')}</strong>
                </div>
                <div class="standing-record-row">
                    <span>Games Played</span>
                    <strong>${Number(team.gamesPlayed || 0)}</strong>
                </div>
            </article>
        `);

        if (index === 7) {
            cardRows.push(`
                <div class="standings-cutoff-card-divider">
                    <span class="playoff-cutoff-tag-card">Playoff Cutoff</span>
                </div>
            `);
        }
    });

    standingsCards.innerHTML = cardRows.join('');
}

function renderStandingsEmpty(message) {
    if (!standingsTableBody || !standingsCards) return;

    if (standingsCount) {
        standingsCount.textContent = '0 Teams';
    }

    standingsTableBody.innerHTML = `
        <tr>
            <td colspan="4" class="standings-empty">${escapeHtml(message)}</td>
        </tr>
    `;

    standingsCards.innerHTML = '';

    if (playoffBracket) {
        playoffBracket.style.display = 'none';
    }
    if (playoffBracketGrid) {
        playoffBracketGrid.innerHTML = '';
    }
}

function renderPlayoffBracket(topEight, seasonId) {
    if (!playoffBracket || !playoffBracketGrid) return;

    if (topEight.length < 8) {
        playoffBracket.style.display = 'block';
        playoffBracketGrid.innerHTML = '<p class="standings-empty">Not enough teams to build the playoff bracket.</p>';
        return;
    }

    const matchups = [
        [topEight[0], topEight[7]],
        [topEight[1], topEight[6]],
        [topEight[2], topEight[5]],
        [topEight[3], topEight[4]],
    ];

    const quarterfinalsData = matchups.map((pair, index) => {
        const highSeed = pair[0];
        const lowSeed = pair[1];
        const resultKey = `${highSeed.team || ''}|${lowSeed.team || ''}`;
        const configuredResult = seasonId === '225' ? PLAYOFF_2026_QUARTERFINAL_RESULTS[resultKey] : null;

        let winnerTeam = null;
        let loserTeam = null;

        if (configuredResult) {
            winnerTeam = configuredResult.winner === 'high' ? highSeed : lowSeed;
            loserTeam = configuredResult.winner === 'high' ? lowSeed : highSeed;
        }

        return {
            index,
            highSeed,
            lowSeed,
            highScore: configuredResult ? configuredResult.highScore : null,
            lowScore: configuredResult ? configuredResult.lowScore : null,
            winnerTeam,
            loserTeam,
        };
    });

    const winnersByName = {};
    quarterfinalsData.forEach((matchup) => {
        if (matchup.winnerTeam?.team) {
            winnersByName[matchup.winnerTeam.team] = matchup.winnerTeam;
        }
    });

    const semifinalOneTeams = [
        winnersByName['Georgia Swarm'],
        winnersByName['Halifax Thunderbirds'],
    ].filter(Boolean);

    const semifinalTwoTeams = [
        winnersByName['Toronto Rock'],
        winnersByName['San Diego Seals'],
    ].filter(Boolean);

    const quarterfinals = quarterfinalsData.map((matchup) => {
        const highSeed = matchup.highSeed;
        const lowSeed = matchup.lowSeed;

        const highName = highSeed.team || 'TBD';
        const lowName = lowSeed.team || 'TBD';
        const highLogo = highSeed.logo || getTeamLogoPath(highName);
        const lowLogo = lowSeed.logo || getTeamLogoPath(lowName);

        return `
            <article class="playoff-matchup-card">
                <h4>Quarterfinal ${matchup.index + 1}</h4>
                <div class="playoff-series-format">Single Game</div>
                <div class="playoff-seed-row">
                    <span class="playoff-seed-number">#${Number(highSeed.rank || 0)}</span>
                    <img class="playoff-seed-logo" src="${escapeHtml(highLogo)}" alt="${escapeHtml(highName)} logo" loading="lazy" onerror="this.src='${DEFAULT_TEAM_LOGO}'; this.onerror=null;">
                    <span class="playoff-seed-name">${escapeHtml(highName)}</span>
                    <span class="playoff-seed-record">${matchup.highScore !== null ? Number(matchup.highScore) : escapeHtml(highSeed.record || '0-0')}</span>
                </div>
                <div class="playoff-vs">vs</div>
                <div class="playoff-seed-row">
                    <span class="playoff-seed-number">#${Number(lowSeed.rank || 0)}</span>
                    <img class="playoff-seed-logo" src="${escapeHtml(lowLogo)}" alt="${escapeHtml(lowName)} logo" loading="lazy" onerror="this.src='${DEFAULT_TEAM_LOGO}'; this.onerror=null;">
                    <span class="playoff-seed-name">${escapeHtml(lowName)}</span>
                    <span class="playoff-seed-record">${matchup.lowScore !== null ? Number(matchup.lowScore) : escapeHtml(lowSeed.record || '0-0')}</span>
                </div>
            </article>
        `;
    }).join('');

    const semifinalOne = semifinalOneTeams.length === 2
        ? `
            <article class="playoff-matchup-card playoff-matchup-placeholder">
                <h4>Semifinal 1</h4>
                <div class="playoff-series-format">Best of 3</div>
                <div class="playoff-seed-row">
                    <span class="playoff-seed-number">#${Number(semifinalOneTeams[0].rank || 0)}</span>
                    <img class="playoff-seed-logo" src="${escapeHtml(semifinalOneTeams[0].logo || getTeamLogoPath(semifinalOneTeams[0].team || ''))}" alt="${escapeHtml(semifinalOneTeams[0].team || 'TBD')} logo" loading="lazy" onerror="this.src='${DEFAULT_TEAM_LOGO}'; this.onerror=null;">
                    <span class="playoff-seed-name">${escapeHtml(semifinalOneTeams[0].team || 'TBD')} <span class="playoff-home-tag">Home</span></span>
                    <span class="playoff-seed-record">${escapeHtml(semifinalOneTeams[0].record || '0-0')}</span>
                </div>
                <div class="playoff-vs">vs</div>
                <div class="playoff-seed-row">
                    <span class="playoff-seed-number">#${Number(semifinalOneTeams[1].rank || 0)}</span>
                    <img class="playoff-seed-logo" src="${escapeHtml(semifinalOneTeams[1].logo || getTeamLogoPath(semifinalOneTeams[1].team || ''))}" alt="${escapeHtml(semifinalOneTeams[1].team || 'TBD')} logo" loading="lazy" onerror="this.src='${DEFAULT_TEAM_LOGO}'; this.onerror=null;">
                    <span class="playoff-seed-name">${escapeHtml(semifinalOneTeams[1].team || 'TBD')}</span>
                    <span class="playoff-seed-record">${escapeHtml(semifinalOneTeams[1].record || '0-0')}</span>
                </div>
            </article>
        `
        : `
            <article class="playoff-matchup-card playoff-matchup-placeholder">
                <h4>Semifinal 1</h4>
                <div class="playoff-series-format">Best of 3</div>
                <div class="playoff-seed-row playoff-seed-row-placeholder">
                    <span class="playoff-seed-number">W1</span>
                    <img class="playoff-seed-logo" src="${DEFAULT_TEAM_LOGO}" alt="Winner QF1 logo" loading="lazy">
                    <span class="playoff-seed-name">Winner Quarterfinal 1</span>
                    <span class="playoff-seed-record">TBD</span>
                </div>
                <div class="playoff-vs">vs</div>
                <div class="playoff-seed-row playoff-seed-row-placeholder">
                    <span class="playoff-seed-number">W2</span>
                    <img class="playoff-seed-logo" src="${DEFAULT_TEAM_LOGO}" alt="Winner QF2 logo" loading="lazy">
                    <span class="playoff-seed-name">Winner Quarterfinal 2</span>
                    <span class="playoff-seed-record">TBD</span>
                </div>
            </article>
        `;

    const semifinalTwo = semifinalTwoTeams.length === 2
        ? `
            <article class="playoff-matchup-card playoff-matchup-placeholder">
                <h4>Semifinal 2</h4>
                <div class="playoff-series-format">Best of 3</div>
                <div class="playoff-seed-row">
                    <span class="playoff-seed-number">#${Number(semifinalTwoTeams[0].rank || 0)}</span>
                    <img class="playoff-seed-logo" src="${escapeHtml(semifinalTwoTeams[0].logo || getTeamLogoPath(semifinalTwoTeams[0].team || ''))}" alt="${escapeHtml(semifinalTwoTeams[0].team || 'TBD')} logo" loading="lazy" onerror="this.src='${DEFAULT_TEAM_LOGO}'; this.onerror=null;">
                    <span class="playoff-seed-name">${escapeHtml(semifinalTwoTeams[0].team || 'TBD')} <span class="playoff-home-tag">Home</span></span>
                    <span class="playoff-seed-record">${escapeHtml(semifinalTwoTeams[0].record || '0-0')}</span>
                </div>
                <div class="playoff-vs">vs</div>
                <div class="playoff-seed-row">
                    <span class="playoff-seed-number">#${Number(semifinalTwoTeams[1].rank || 0)}</span>
                    <img class="playoff-seed-logo" src="${escapeHtml(semifinalTwoTeams[1].logo || getTeamLogoPath(semifinalTwoTeams[1].team || ''))}" alt="${escapeHtml(semifinalTwoTeams[1].team || 'TBD')} logo" loading="lazy" onerror="this.src='${DEFAULT_TEAM_LOGO}'; this.onerror=null;">
                    <span class="playoff-seed-name">${escapeHtml(semifinalTwoTeams[1].team || 'TBD')}</span>
                    <span class="playoff-seed-record">${escapeHtml(semifinalTwoTeams[1].record || '0-0')}</span>
                </div>
            </article>
        `
        : `
            <article class="playoff-matchup-card playoff-matchup-placeholder">
                <h4>Semifinal 2</h4>
                <div class="playoff-series-format">Best of 3</div>
                <div class="playoff-seed-row playoff-seed-row-placeholder">
                    <span class="playoff-seed-number">W3</span>
                    <img class="playoff-seed-logo" src="${DEFAULT_TEAM_LOGO}" alt="Winner QF3 logo" loading="lazy">
                    <span class="playoff-seed-name">Winner Quarterfinal 3</span>
                    <span class="playoff-seed-record">TBD</span>
                </div>
                <div class="playoff-vs">vs</div>
                <div class="playoff-seed-row playoff-seed-row-placeholder">
                    <span class="playoff-seed-number">W4</span>
                    <img class="playoff-seed-logo" src="${DEFAULT_TEAM_LOGO}" alt="Winner QF4 logo" loading="lazy">
                    <span class="playoff-seed-name">Winner Quarterfinal 4</span>
                    <span class="playoff-seed-record">TBD</span>
                </div>
            </article>
        `;

    playoffBracket.style.display = 'block';
    playoffBracketGrid.innerHTML = `
        <div class="playoff-round playoff-round-quarterfinals">
            <div class="playoff-round-label">Quarterfinals</div>
            ${quarterfinals}
        </div>
        <div class="playoff-round playoff-round-semifinals">
            <div class="playoff-round-label">Semifinals</div>
            ${semifinalOne}
            ${semifinalTwo}
        </div>
        <div class="playoff-round playoff-round-final">
            <div class="playoff-round-label">Championship</div>
            <article class="playoff-matchup-card playoff-matchup-final">
                <h4>NLL Final</h4>
                <div class="playoff-series-format">Best of 3</div>
                <div class="playoff-seed-row playoff-seed-row-placeholder">
                    <span class="playoff-seed-number">W</span>
                    <img class="playoff-seed-logo" src="${DEFAULT_TEAM_LOGO}" alt="Finalist 1 logo" loading="lazy">
                    <span class="playoff-seed-name">Winner Semifinal 1</span>
                    <span class="playoff-seed-record">TBD</span>
                </div>
                <div class="playoff-vs">vs</div>
                <div class="playoff-seed-row playoff-seed-row-placeholder">
                    <span class="playoff-seed-number">W</span>
                    <img class="playoff-seed-logo" src="${DEFAULT_TEAM_LOGO}" alt="Finalist 2 logo" loading="lazy">
                    <span class="playoff-seed-name">Winner Semifinal 2</span>
                    <span class="playoff-seed-record">TBD</span>
                </div>
            </article>
        </div>
    `;
}

async function loadSchedule() {
    if (!scheduleTableBody || !scheduleLoading) return;

    const seasonId = scheduleSeasonFilter ? scheduleSeasonFilter.value : '225';
    const stage = scheduleStageFilter ? scheduleStageFilter.value : 'REG';
    const week = scheduleWeekFilter ? scheduleWeekFilter.value : 'all';
    const team = scheduleTeamFilter ? scheduleTeamFilter.value : '';

    try {
        scheduleLoading.style.display = 'block';
        renderScheduleEmpty('Loading schedule...');

        const params = new URLSearchParams({
            season_id: seasonId,
            stage,
            week,
            team,
        });

        const response = await fetch(`${API_BASE}/schedule?${params.toString()}`);
        if (!response.ok) {
            throw new Error('Failed to load schedule data');
        }

        const rows = await response.json();
        renderScheduleRows(rows);
        scheduleLoaded = true;
    } catch (error) {
        console.error('Error loading schedule:', error);
        renderScheduleEmpty('Unable to load schedule data right now.');
    } finally {
        scheduleLoading.style.display = 'none';
    }
}

function renderScheduleRows(rows) {
    if (!scheduleTableBody) return;

    if (!rows.length) {
        renderScheduleEmpty('No games found for the selected filters.');
        return;
    }

    scheduleTableBody.innerHTML = rows.map((game) => {
        const recapCell = game.recapLink
            ? `<a class="schedule-recap-link" href="${escapeHtml(game.recapLink)}" target="_blank" rel="noopener noreferrer">View</a>`
            : 'N/A';

        return `
            <tr>
                <td>${escapeHtml(game.date)}</td>
                <td>${escapeHtml(game.awayTeam)}</td>
                <td>${escapeHtml(game.homeTeam)}</td>
                <td>${escapeHtml(game.result)}</td>
                <td>${escapeHtml(game.venue)}</td>
                <td>${escapeHtml(game.status)}</td>
                <td>${recapCell}</td>
            </tr>
        `;
    }).join('');
}

function renderScheduleEmpty(message) {
    if (!scheduleTableBody) return;

    scheduleTableBody.innerHTML = `
        <tr>
            <td colspan="7" class="schedule-empty">${escapeHtml(message)}</td>
        </tr>
    `;
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
        setFilterOptions(allPlayers);
        applyFilters();
    } catch (error) {
        console.error('Error loading players:', error);
        showErrorMessage('Failed to load player data. Please try again.');
    } finally {
        loadingSpinner.style.display = 'none';
    }
}

function setFilterOptions(players) {
    const teams = [...new Set(players.map(player => player.team).filter(Boolean))]
        .sort((a, b) => a.localeCompare(b));
    const seasons = [...new Set(players.map(player => player.season).filter(Boolean))]
        .sort((a, b) => b - a);

    teamFilter.innerHTML = '<option value="all">All Teams</option>';
    teams.forEach(team => {
        teamFilter.innerHTML += `<option value="${escapeHtml(team)}">${escapeHtml(team)}</option>`;
    });

    seasonFilter.innerHTML = '<option value="all">All Seasons</option>';
    seasons.forEach(season => {
        seasonFilter.innerHTML += `<option value="${season}">${season}</option>`;
    });
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

    const teamColors = getTeamColors(player.team);
    card.style.setProperty('--team-primary', teamColors.primary);
    card.style.setProperty('--team-secondary', teamColors.secondary);
    card.style.setProperty('--team-accent', teamColors.accent);
    card.style.setProperty('--team-primary-contrast', getContrastColor(teamColors.primary));
    card.style.setProperty('--team-secondary-contrast', getContrastColor(teamColors.secondary));
    card.style.setProperty('--team-accent-contrast', getContrastColor(teamColors.accent));
    card.style.setProperty('--team-tint', hexToRgba(teamColors.secondary, 0.08));
    card.style.setProperty('--team-glow', hexToRgba(teamColors.accent, 0.16));

    const goalsEarned = player.goals || 0;
    const assistsEarned = player.assists || 0;
    const pointsTotal = player.points || 0;
    const isGoaltender = (player.position || '').toUpperCase() === 'GOALTENDER';
    const gaaValue = typeof player.goals_against_average === 'number'
        ? player.goals_against_average.toFixed(2)
        : 'N/A';
    const savePctValue = typeof player.save_percentage === 'number'
        ? `${player.save_percentage.toFixed(1)}%`
        : 'N/A';
    const minutesPlayedValue = player.minutes_played || 'N/A';
    const teamName = player.team || 'N/A';
    const teamLogoPath = getTeamLogoPath(teamName);
    card.style.setProperty('--team-logo-url', `url("${teamLogoPath}")`);

    const statsMarkup = isGoaltender ? `
            <div class="stat-item">
                <div class="stat-label">Wins</div>
                <div class="stat-value">${player.wins || 0}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">GAA</div>
                <div class="stat-value">${gaaValue}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Save %</div>
                <div class="stat-value">${savePctValue}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Minutes Played</div>
                <div class="stat-value">${minutesPlayedValue}</div>
            </div>
    ` : `
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
    `;

    card.innerHTML = `
        <div class="card-team-logo-wrap">
            <img class="team-logo-card" src="${teamLogoPath}" alt="${escapeHtml(teamName)} logo" loading="lazy" onerror="this.src='${DEFAULT_TEAM_LOGO}'; this.onerror=null;">
        </div>
        <div class="player-header">
            <div class="player-name">${escapeHtml(player.player_name || 'Unknown')}</div>
            <span class="player-position">${escapeHtml(getPositionLabel(player.position))}</span>
            <div class="player-team">${escapeHtml(teamName)}</div>
        </div>
        <div class="player-stats">
            ${statsMarkup}
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
        const modalTeamColors = getTeamColors(playerData.profile?.team);

        modalBody.style.setProperty('--modal-primary', modalTeamColors.primary);
        modalBody.style.setProperty('--modal-secondary', modalTeamColors.secondary);
        modalBody.style.setProperty('--modal-accent', modalTeamColors.accent);
        modalBody.style.setProperty('--modal-secondary-contrast', getContrastColor(modalTeamColors.secondary));
        modalBody.style.setProperty('--modal-stat-bg', hexToRgba(modalTeamColors.secondary, 0.08));

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
    const teamName = profile.team || 'N/A';
    const teamLogoPath = getTeamLogoPath(teamName);

    if (!stats.games_played) {
        return `
            <div class="modal-header">
                <div class="modal-team-brand">
                    <img class="modal-team-logo" src="${teamLogoPath}" alt="${escapeHtml(teamName)} logo" loading="lazy" onerror="this.src='${DEFAULT_TEAM_LOGO}'; this.onerror=null;">
                </div>
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
            <div class="modal-team-brand">
                <img class="modal-team-logo" src="${teamLogoPath}" alt="${escapeHtml(teamName)} logo" loading="lazy" onerror="this.src='${DEFAULT_TEAM_LOGO}'; this.onerror=null;">
            </div>
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
    applyFilters();
}

function sortPlayers(players, selectedPosition) {
    const normalizedPosition = String(selectedPosition || 'all').toUpperCase();
    const sortMetric = POSITION_SORT_METRICS[normalizedPosition] || 'points';

    return [...players].sort((left, right) => {
        const metricDifference = Number(right[sortMetric] || 0) - Number(left[sortMetric] || 0);
        if (metricDifference !== 0) {
            return metricDifference;
        }

        const pointsDifference = Number(right.points || 0) - Number(left.points || 0);
        if (pointsDifference !== 0) {
            return pointsDifference;
        }

        const gamesPlayedDifference = Number(right.games_played || 0) - Number(left.games_played || 0);
        if (gamesPlayedDifference !== 0) {
            return gamesPlayedDifference;
        }

        return (left.player_name || '').localeCompare(right.player_name || '');
    });
}

function applyFilters() {
    const query = searchInput.value.toLowerCase().trim();
    const selectedTeam = teamFilter.value;
    const selectedSeason = seasonFilter.value;
    const selectedPosition = positionFilter.value;

    filteredPlayers = allPlayers.filter(player => {
        const matchesSearch = !query || (
            (player.player_name && player.player_name.toLowerCase().includes(query)) ||
            (player.team && player.team.toLowerCase().includes(query)) ||
            (player.position && player.position.toLowerCase().includes(query))
        );

        const matchesTeam = selectedTeam === 'all' || player.team === selectedTeam;
        const matchesSeason = selectedSeason === 'all' || String(player.season) === selectedSeason;
        const matchesPosition = selectedPosition === 'all' ||
            (player.position && player.position.toUpperCase() === selectedPosition);

        return matchesSearch && matchesTeam && matchesSeason && matchesPosition;
    });

    filteredPlayers = sortPlayers(filteredPlayers, selectedPosition);

    displayPlayers(filteredPlayers);
}

// Reset filters
function resetFilters() {
    searchInput.value = '';
    teamFilter.value = 'all';
    seasonFilter.value = 'all';
    positionFilter.value = 'all';
    applyFilters();
}

// Close modal
function closeModal() {
    playerModal.classList.remove('show');
    const modalBody = document.getElementById('modalBody');
    modalBody.innerHTML = '';
    modalBody.removeAttribute('style');
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

function getTeamColors(teamName) {
    const fallback = {
        primary: '#C8102E',
        secondary: '#1A1A1A',
        accent: '#FFC72C'
    };

    if (!teamName) return fallback;

    const normalized = normalizeTeamName(teamName);
    let colorSet = TEAM_COLOR_SCHEMES[normalized];

    if (!colorSet && TEAM_ALIASES[normalized]) {
        colorSet = TEAM_COLOR_SCHEMES[TEAM_ALIASES[normalized]];
    }

    if (!colorSet) {
        const partialMatch = Object.keys(TEAM_ALIASES).find(alias => normalized.includes(alias));
        if (partialMatch) {
            colorSet = TEAM_COLOR_SCHEMES[TEAM_ALIASES[partialMatch]];
        }
    }

    if (!colorSet) return fallback;

    const basePrimary = colorSet[0] || fallback.primary;
    const secondary = colorSet[1] || colorSet[0] || fallback.secondary;
    const accent = colorSet[2] || colorSet[1] || colorSet[0] || fallback.accent;

    return {
        primary: isLightColor(basePrimary) ? secondary : basePrimary,
        secondary,
        accent,
    };
}

function getTeamLogoPath(teamName) {
    if (!teamName) return DEFAULT_TEAM_LOGO;

    const normalized = normalizeTeamName(teamName);
    let logoFile = TEAM_LOGOS[normalized];

    if (!logoFile && TEAM_ALIASES[normalized]) {
        logoFile = TEAM_LOGOS[TEAM_ALIASES[normalized]];
    }

    if (!logoFile) {
        const partialMatch = Object.keys(TEAM_ALIASES).find(alias => normalized.includes(alias));
        if (partialMatch) {
            logoFile = TEAM_LOGOS[TEAM_ALIASES[partialMatch]];
        }
    }

    return logoFile ? `team-logos/${encodeURIComponent(logoFile)}` : DEFAULT_TEAM_LOGO;
}

function normalizeTeamName(value) {
    return String(value || '')
        .toLowerCase()
        .replace(/[^a-z0-9 ]+/g, '')
        .replace(/\s+/g, ' ')
        .trim();
}

function hexToRgba(hex, alpha) {
    const cleaned = String(hex || '').replace('#', '').trim();
    if (!/^[0-9a-fA-F]{6}$/.test(cleaned)) {
        return `rgba(26, 26, 26, ${alpha})`;
    }

    const r = parseInt(cleaned.slice(0, 2), 16);
    const g = parseInt(cleaned.slice(2, 4), 16);
    const b = parseInt(cleaned.slice(4, 6), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function getContrastColor(hex) {
    const cleaned = String(hex || '').replace('#', '').trim();
    if (!/^[0-9a-fA-F]{6}$/.test(cleaned)) return '#FFFFFF';

    const r = parseInt(cleaned.slice(0, 2), 16);
    const g = parseInt(cleaned.slice(2, 4), 16);
    const b = parseInt(cleaned.slice(4, 6), 16);

    const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
    return luminance > 0.6 ? '#111111' : '#FFFFFF';
}

function isLightColor(hex) {
    const cleaned = String(hex || '').replace('#', '').trim();
    if (!/^[0-9a-fA-F]{6}$/.test(cleaned)) return false;

    const r = parseInt(cleaned.slice(0, 2), 16);
    const g = parseInt(cleaned.slice(2, 4), 16);
    const b = parseInt(cleaned.slice(4, 6), 16);
    const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;

    return luminance > 0.85;
}

// Helper: Escape HTML
function escapeHtml(text) {
    const safeText = String(text ?? '');
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return safeText.replace(/[&<>"']/g, m => map[m]);
}

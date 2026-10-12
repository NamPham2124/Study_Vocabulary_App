"""Built-in Interactive Web UI for VocabMaster."""

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>VocabMaster - Spaced Repetition Learning</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            brand: {
              50: '#f0fdf4',
              100: '#dcfce7',
              500: '#22c55e',
              600: '#16a34a',
              700: '#15803d',
            }
          }
        }
      }
    }
  </script>
  <style>
    .card-flip {
      perspective: 1000px;
    }
    .flashcard {
      transition: transform 0.3s ease;
    }
  </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col font-sans">

  <!-- Top Navbar -->
  <header class="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-40">
    <div class="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
      <div class="flex items-center space-x-3 cursor-pointer" onclick="showDashboard()">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-emerald-400 flex items-center justify-center text-white shadow-lg shadow-brand-500/20">
          <i class="fa-solid fa-graduation-cap text-lg"></i>
        </div>
        <div>
          <span class="text-xl font-bold tracking-tight bg-gradient-to-r from-emerald-400 to-teal-300 bg-clip-text text-transparent">VocabMaster</span>
          <span class="text-xs px-2 py-0.5 ml-1.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">SRS v1.0</span>
        </div>
      </div>

      <div class="flex items-center space-x-3">
        <a href="/docs" target="_blank" class="px-3 py-1.5 text-xs font-medium text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-lg transition border border-slate-700 flex items-center gap-1.5">
          <i class="fa-solid fa-book-code"></i> API Docs (/docs)
        </a>

        <div id="authControls" class="flex items-center space-x-2">
          <!-- Will be updated by JS -->
        </div>
      </div>
    </div>
  </header>

  <!-- Main Content Container -->
  <main class="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">
    
    <!-- AUTHENTICATION VIEW -->
    <div id="authView" class="max-w-md mx-auto my-12 bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-2xl">
      <div class="text-center mb-6">
        <h2 id="authTitle" class="text-2xl font-bold text-white mb-1">Welcome to VocabMaster</h2>
        <p class="text-sm text-slate-400">Master vocabulary with scientifically proven spaced repetition</p>
      </div>

      <div class="flex border-b border-slate-800 mb-6">
        <button id="tabLogin" onclick="switchAuthTab('login')" class="flex-1 pb-3 text-sm font-semibold border-b-2 border-emerald-500 text-emerald-400">Log In</button>
        <button id="tabRegister" onclick="switchAuthTab('register')" class="flex-1 pb-3 text-sm font-semibold border-b-2 border-transparent text-slate-400 hover:text-slate-200">Register</button>
      </div>

      <form id="authForm" onsubmit="handleAuthSubmit(event)" class="space-y-4">
        <div id="usernameGroup" class="hidden">
          <label class="block text-xs font-medium text-slate-300 mb-1">Username</label>
          <input type="text" id="authUsername" class="w-full px-3.5 py-2.5 rounded-lg bg-slate-800 border border-slate-700 text-white focus:outline-none focus:border-emerald-500 text-sm" placeholder="john_doe">
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-300 mb-1">Email</label>
          <input type="email" id="authEmail" required class="w-full px-3.5 py-2.5 rounded-lg bg-slate-800 border border-slate-700 text-white focus:outline-none focus:border-emerald-500 text-sm" placeholder="user@example.com">
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-300 mb-1">Password</label>
          <input type="password" id="authPassword" required class="w-full px-3.5 py-2.5 rounded-lg bg-slate-800 border border-slate-700 text-white focus:outline-none focus:border-emerald-500 text-sm" placeholder="••••••••">
        </div>
        <div id="authError" class="text-xs text-rose-400 hidden p-2 bg-rose-500/10 rounded border border-rose-500/20"></div>
        <button type="submit" id="authSubmitBtn" class="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-medium text-sm transition shadow-lg shadow-emerald-600/30">
          Sign In
        </button>
      </form>

      <div class="mt-6 pt-6 border-t border-slate-800 text-center">
        <button onclick="quickDemoLogin()" class="w-full py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white rounded-lg text-xs font-medium border border-slate-700 transition flex items-center justify-center gap-2">
          <i class="fa-solid fa-bolt text-amber-400"></i> Quick Test (1-Click Demo Login)
        </button>
      </div>
    </div>

    <!-- DASHBOARD VIEW -->
    <div id="dashboardView" class="hidden space-y-6">
      <!-- Top banner & stats -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 class="text-2xl font-bold text-white flex items-center gap-2">
            <span>Vocabulary Decks</span>
          </h1>
          <p class="text-sm text-slate-400">Review due flashcards and expand your linguistic knowledge</p>
        </div>
        <div class="flex items-center gap-3">
          <button onclick="startDailyGlobalSession()" class="px-4 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-sm font-semibold shadow-lg shadow-emerald-600/30 transition flex items-center gap-2">
            <i class="fa-solid fa-play"></i> Study All Due Cards
          </button>
          <button onclick="openCreateDeckModal()" class="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-xl text-sm font-medium transition flex items-center gap-2">
            <i class="fa-solid fa-plus"></i> New Deck
          </button>
        </div>
      </div>

      <!-- Stats Bar -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-4">
          <div class="text-xs text-slate-400 font-medium mb-1">Total Decks</div>
          <div id="statTotalDecks" class="text-2xl font-bold text-white">0</div>
        </div>
        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-4">
          <div class="text-xs text-slate-400 font-medium mb-1">Total Cards</div>
          <div id="statTotalCards" class="text-2xl font-bold text-teal-400">0</div>
        </div>
        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-4">
          <div class="text-xs text-slate-400 font-medium mb-1">Due Reviews Today</div>
          <div id="statDueCards" class="text-2xl font-bold text-amber-400">0</div>
        </div>
        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-4">
          <div class="text-xs text-slate-400 font-medium mb-1">New Cards Ready</div>
          <div id="statNewCards" class="text-2xl font-bold text-emerald-400">0</div>
        </div>
      </div>

      <!-- Active / Recoverable Session Banner -->
      <div id="activeSessionBanner" class="hidden bg-gradient-to-r from-amber-950/40 via-amber-900/20 to-slate-900 border border-amber-500/30 rounded-2xl p-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center text-lg">
            <i class="fa-solid fa-rotate-left"></i>
          </div>
          <div>
            <div class="font-semibold text-amber-200 text-sm">Recoverable Study Session Found!</div>
            <div id="activeSessionDesc" class="text-xs text-amber-300/70">Session was paused or interrupted. You can resume exactly where you left off.</div>
          </div>
        </div>
        <button onclick="resumeActiveSession()" class="px-4 py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 font-semibold rounded-lg text-xs transition">
          Resume Session
        </button>
      </div>

      <!-- Decks Grid -->
      <div id="decksGrid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        <!-- Decks inserted via JavaScript -->
      </div>
    </div>

    <!-- STUDY SESSION VIEW -->
    <div id="studyView" class="hidden max-w-2xl mx-auto space-y-6">
      <!-- Session Header -->
      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-4 flex items-center justify-between">
        <div class="flex-1 mr-4">
          <div class="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span id="sessionDeckTitle" class="font-medium text-slate-200">Study Session</span>
            <span id="sessionProgressText">Card 1 of 10</span>
          </div>
          <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
            <div id="sessionProgressBar" class="bg-gradient-to-r from-emerald-500 to-teal-400 h-full transition-all duration-300" style="width: 10%"></div>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <button onclick="pauseStudySession()" title="Pause Session" class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs border border-slate-700 transition">
            <i class="fa-solid fa-pause"></i> Pause
          </button>
          <button onclick="abandonStudySession()" title="Exit" class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-rose-400 rounded-lg text-xs border border-slate-700 transition">
            <i class="fa-solid fa-xmark"></i> Exit
          </button>
        </div>
      </div>

      <!-- Active Flashcard -->
      <div id="flashcardContainer" class="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl relative min-h-[380px] flex flex-col justify-between">
        <!-- Top Card Badges -->
        <div class="flex items-center justify-between mb-4">
          <span id="cardLangBadge" class="px-2.5 py-1 rounded-md text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 uppercase">EN</span>
          <div class="flex items-center gap-2">
            <span id="cardStateBadge" class="px-2.5 py-1 rounded-md text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700">NEW</span>
            <button onclick="speakCurrentWord()" title="Listen Pronunciation" class="w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white flex items-center justify-center transition border border-slate-700">
              <i class="fa-solid fa-volume-high text-xs"></i>
            </button>
          </div>
        </div>

        <!-- Word / Question Section -->
        <div class="my-auto text-center py-6">
          <div id="cardReading" class="text-sm font-medium text-emerald-400 mb-1 hidden"></div>
          <div id="cardTerm" class="text-4xl sm:text-5xl font-black text-white tracking-tight mb-2">Word</div>
          <div id="cardIpa" class="text-sm text-slate-400 font-mono tracking-wider">/ipa/</div>
          
          <!-- Language Specific Badges -->
          <div id="cardLangFields" class="flex flex-wrap items-center justify-center gap-2 mt-4"></div>
        </div>

        <!-- Answer / Definition Section (Hidden until flipped) -->
        <div id="answerSection" class="hidden mt-6 pt-6 border-t border-slate-800/80 animate-fade-in">
          <div class="text-center mb-6">
            <div id="cardPos" class="inline-block px-2.5 py-0.5 rounded text-xs font-semibold bg-teal-500/10 text-teal-300 border border-teal-500/20 mb-2">noun</div>
            <div id="cardDefinition" class="text-2xl font-bold text-emerald-200">Definition meaning here</div>
          </div>

          <!-- Examples & Notes -->
          <div id="cardExamplesBox" class="bg-slate-950/60 rounded-xl p-4 border border-slate-800/60 mb-6 text-sm text-slate-300 space-y-2 text-left hidden">
            <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Examples:</div>
            <ul id="cardExamplesList" class="list-disc list-inside space-y-1 text-slate-300 text-sm"></ul>
          </div>

          <!-- SRS Rating Buttons (0 to 5) -->
          <div>
            <div class="text-xs text-slate-400 text-center mb-2 font-medium">How well did you recall this? (Keys 0-5)</div>
            <div class="grid grid-cols-3 sm:grid-cols-6 gap-2">
              <button onclick="rateCard(0)" class="py-2.5 bg-rose-950/40 hover:bg-rose-900/60 border border-rose-800/50 rounded-xl text-center transition group">
                <div class="text-xs font-bold text-rose-400">0</div>
                <div class="text-[10px] text-rose-300/70">Blackout</div>
              </button>
              <button onclick="rateCard(1)" class="py-2.5 bg-orange-950/40 hover:bg-orange-900/60 border border-orange-800/50 rounded-xl text-center transition group">
                <div class="text-xs font-bold text-orange-400">1</div>
                <div class="text-[10px] text-orange-300/70">Forgot</div>
              </button>
              <button onclick="rateCard(2)" class="py-2.5 bg-amber-950/40 hover:bg-amber-900/60 border border-amber-800/50 rounded-xl text-center transition group">
                <div class="text-xs font-bold text-amber-400">2</div>
                <div class="text-[10px] text-amber-300/70">Hard</div>
              </button>
              <button onclick="rateCard(3)" class="py-2.5 bg-lime-950/40 hover:bg-lime-900/60 border border-lime-800/50 rounded-xl text-center transition group">
                <div class="text-xs font-bold text-lime-400">3</div>
                <div class="text-[10px] text-lime-300/70">Passed</div>
              </button>
              <button onclick="rateCard(4)" class="py-2.5 bg-emerald-950/40 hover:bg-emerald-900/60 border border-emerald-800/50 rounded-xl text-center transition group">
                <div class="text-xs font-bold text-emerald-400">4</div>
                <div class="text-[10px] text-emerald-300/70">Good</div>
              </button>
              <button onclick="rateCard(5)" class="py-2.5 bg-teal-950/40 hover:bg-teal-900/60 border border-teal-800/50 rounded-xl text-center transition group">
                <div class="text-xs font-bold text-teal-400">5</div>
                <div class="text-[10px] text-teal-300/70">Easy</div>
              </button>
            </div>
          </div>
        </div>

        <!-- Reveal Button (Before flipped) -->
        <div id="revealBtnContainer" class="mt-8 text-center">
          <button onclick="revealAnswer()" class="w-full py-3.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-bold text-base transition shadow-lg shadow-emerald-600/30 flex items-center justify-center gap-2">
            <span>Show Answer</span>
            <kbd class="px-2 py-0.5 text-xs bg-emerald-700/60 rounded border border-emerald-500/40 font-mono">Space</kbd>
          </button>
        </div>
      </div>
    </div>

    <!-- SESSION COMPLETED MODAL -->
    <div id="summaryModal" class="hidden fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div class="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 max-w-md w-full shadow-2xl text-center space-y-6">
        <div class="w-16 h-16 rounded-2xl bg-emerald-500/20 text-emerald-400 mx-auto flex items-center justify-center text-3xl">
          <i class="fa-solid fa-trophy"></i>
        </div>
        <div>
          <h3 class="text-2xl font-bold text-white mb-1">Session Completed!</h3>
          <p class="text-sm text-slate-400">All due cards in this session have been reviewed.</p>
        </div>

        <div class="grid grid-cols-2 gap-3 bg-slate-950/60 p-4 rounded-2xl border border-slate-800">
          <div>
            <div class="text-xs text-slate-400 mb-1">Cards Studied</div>
            <div id="summaryCardsCount" class="text-xl font-bold text-white">0</div>
          </div>
          <div>
            <div class="text-xs text-slate-400 mb-1">Accuracy</div>
            <div id="summaryAccuracy" class="text-xl font-bold text-emerald-400">0%</div>
          </div>
        </div>

        <button onclick="closeSummaryModal()" class="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-xl text-sm transition">
          Return to Dashboard
        </button>
      </div>
    </div>

    <!-- CREATE DECK MODAL -->
    <div id="createDeckModal" class="hidden fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-md w-full shadow-2xl">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold text-white">Create New Deck</h3>
          <button onclick="closeCreateDeckModal()" class="text-slate-400 hover:text-white"><i class="fa-solid fa-xmark"></i></button>
        </div>
        <form onsubmit="handleCreateDeck(event)" class="space-y-4">
          <div>
            <label class="block text-xs font-medium text-slate-300 mb-1">Deck Name</label>
            <input type="text" id="newDeckName" required class="w-full px-3.5 py-2.5 rounded-lg bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-emerald-500" placeholder="e.g. JLPT N5 Vocabulary">
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-300 mb-1">Target Language</label>
            <select id="newDeckLang" class="w-full px-3.5 py-2.5 rounded-lg bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-emerald-500">
              <option value="en">English (en)</option>
              <option value="ja">Japanese (ja)</option>
              <option value="de">German (de)</option>
              <option value="es">Spanish (es)</option>
              <option value="fr">French (fr)</option>
              <option value="vi">Vietnamese (vi)</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-300 mb-1">Description (optional)</label>
            <input type="text" id="newDeckDesc" class="w-full px-3.5 py-2.5 rounded-lg bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-emerald-500" placeholder="e.g. Essential everyday expressions">
          </div>
          <button type="submit" class="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-medium rounded-lg text-sm transition">
            Create Deck
          </button>
        </form>
      </div>
    </div>

    <!-- IMPORT MODAL -->
    <div id="importModal" class="hidden fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-lg w-full shadow-2xl">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold text-white">Import Words (CSV / XLSX)</h3>
          <button onclick="closeImportModal()" class="text-slate-400 hover:text-white"><i class="fa-solid fa-xmark"></i></button>
        </div>
        <form onsubmit="handleImportSubmit(event)" class="space-y-4">
          <input type="hidden" id="importDeckId">
          <div>
            <label class="block text-xs font-medium text-slate-300 mb-1">Select File (.csv or .xlsx)</label>
            <input type="file" id="importFileInput" required accept=".csv,.xlsx" class="w-full text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-emerald-600 file:text-white hover:file:bg-emerald-500 cursor-pointer">
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-300 mb-1">Deduplication Strategy</label>
            <select id="importDedupStrategy" class="w-full px-3.5 py-2 rounded-lg bg-slate-800 border border-slate-700 text-white text-xs">
              <option value="skip">Skip if word already exists</option>
              <option value="overwrite">Overwrite existing definitions</option>
              <option value="allow_duplicates">Allow duplicate words</option>
            </select>
          </div>
          <div id="importResultBox" class="hidden p-3 rounded-lg text-xs bg-slate-800 border border-slate-700"></div>
          <div class="flex items-center gap-2 pt-2">
            <button type="button" onclick="downloadSampleCSV()" class="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs border border-slate-700 flex items-center gap-1.5">
              <i class="fa-solid fa-download"></i> Sample CSV
            </button>
            <button type="submit" id="importBtn" class="flex-1 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-medium rounded-lg text-xs transition">
              Upload & Import
            </button>
          </div>
        </form>
      </div>
    </div>

  </main>

  <!-- JavaScript Single Page Application Logic -->
  <script>
    let authToken = localStorage.getItem('vocabmaster_token') || null;
    let currentUser = null;
    let currentSession = null;
    let currentCard = null;
    let cardFlipped = false;
    let cardStartTime = Date.now();

    // Check token on load
    window.addEventListener('DOMContentLoaded', async () => {
      if (authToken) {
        try {
          await fetchUserProfile();
          await loadDashboard();
        } catch (e) {
          logout();
        }
      } else {
        showAuth();
      }

      // Keyboard shortcuts for study mode
      window.addEventListener('keydown', (e) => {
        if (document.getElementById('studyView').classList.contains('hidden')) return;
        if (e.code === 'Space' && !cardFlipped) {
          e.preventDefault();
          revealAnswer();
        } else if (cardFlipped && ['0','1','2','3','4','5'].includes(e.key)) {
          e.preventDefault();
          rateCard(parseInt(e.key));
        }
      });
    });

    async function apiRequest(endpoint, options = {}) {
      const headers = options.headers || {};
      if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
      }
      if (!options.isFormData && !headers['Content-Type']) {
        headers['Content-Type'] = 'application/json';
      }

      const res = await fetch(endpoint, { ...options, headers });
      if (res.status === 401) {
        logout();
        throw new Error('Unauthorized');
      }
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'API Request failed');
      }
      return data;
    }

    async function fetchUserProfile() {
      currentUser = await apiRequest('/api/auth/me');
      updateAuthUI();
    }

    function updateAuthUI() {
      const el = document.getElementById('authControls');
      if (currentUser) {
        el.innerHTML = `
          <div class="flex items-center space-x-2 text-xs">
            <span class="text-slate-300 font-medium"><i class="fa-solid fa-user-circle mr-1 text-emerald-400"></i> ${currentUser.username}</span>
            <button onclick="logout()" class="px-2.5 py-1 text-xs bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white rounded-md border border-slate-700 transition">Logout</button>
          </div>
        `;
      } else {
        el.innerHTML = `
          <button onclick="showAuth()" class="px-3 py-1.5 text-xs bg-emerald-600 hover:bg-emerald-500 text-white font-medium rounded-lg transition">Sign In</button>
        `;
      }
    }

    function switchAuthTab(tab) {
      const isLogin = tab === 'login';
      document.getElementById('tabLogin').className = isLogin ? 'flex-1 pb-3 text-sm font-semibold border-b-2 border-emerald-500 text-emerald-400' : 'flex-1 pb-3 text-sm font-semibold border-b-2 border-transparent text-slate-400';
      document.getElementById('tabRegister').className = !isLogin ? 'flex-1 pb-3 text-sm font-semibold border-b-2 border-emerald-500 text-emerald-400' : 'flex-1 pb-3 text-sm font-semibold border-b-2 border-transparent text-slate-400';
      document.getElementById('usernameGroup').classList.toggle('hidden', isLogin);
      document.getElementById('authSubmitBtn').textContent = isLogin ? 'Sign In' : 'Create Account';
      document.getElementById('authError').classList.add('hidden');
    }

    async function handleAuthSubmit(e) {
      e.preventDefault();
      const isRegister = !document.getElementById('usernameGroup').classList.contains('hidden');
      const email = document.getElementById('authEmail').value.trim();
      const password = document.getElementById('authPassword').value;
      const username = document.getElementById('authUsername').value.trim();
      const errBox = document.getElementById('authError');

      try {
        errBox.classList.add('hidden');
        let res;
        if (isRegister) {
          res = await apiRequest('/api/auth/register', {
            method: 'POST',
            body: JSON.stringify({ email, password, username })
          });
        } else {
          res = await apiRequest('/api/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
          });
        }

        authToken = res.access_token;
        localStorage.setItem('vocabmaster_token', authToken);
        await fetchUserProfile();
        await loadDashboard();
      } catch (err) {
        errBox.textContent = err.message;
        errBox.classList.remove('hidden');
      }
    }

    async function quickDemoLogin() {
      // Automatic login to test account or register if not existing
      const demoEmail = 'learner@example.com';
      const demoPassword = 'Password123!';
      try {
        const res = await apiRequest('/api/auth/login', {
          method: 'POST',
          body: JSON.stringify({ email: demoEmail, password: demoPassword })
        });
        authToken = res.access_token;
        localStorage.setItem('vocabmaster_token', authToken);
        await fetchUserProfile();
        await loadDashboard();
      } catch (err) {
        // If demo user does not exist, register them
        const reg = await apiRequest('/api/auth/register', {
          method: 'POST',
          body: JSON.stringify({ username: 'learner', email: demoEmail, password: demoPassword })
        });
        authToken = reg.access_token;
        localStorage.setItem('vocabmaster_token', authToken);
        await fetchUserProfile();

        // Seed with a starter deck
        const deck = await apiRequest('/api/decks', {
          method: 'POST',
          body: JSON.stringify({ name: 'English Tech Vocabulary', target_language: 'en', description: 'Starter essential terms' })
        });

        // Seed sample words
        const sampleCSV = "term,definition,ipa,part_of_speech\\niteration,the repetition of a process in computer algorithms,/ˌɪt.əˈreɪ.ʃən/,noun\\nconcurrency,the execution of multiple instruction sequences simultaneously,/kənˈkʌr.ən.si/,noun\\npersistence,the characteristic of state outliving the process that created it,/pəˈsɪs.təns/,noun\\nheuristic,a problem-solving technique using practical methods,/hjʊəˈrɪs.tɪk/,adjective";
        const blob = new Blob([sampleCSV], { type: 'text/csv' });
        const formData = new FormData();
        formData.append('file', blob, 'sample.csv');
        await apiRequest(`/api/decks/${deck.id}/import`, {
          method: 'POST',
          body: formData,
          isFormData: true
        });

        await loadDashboard();
      }
    }

    function logout() {
      authToken = null;
      currentUser = null;
      localStorage.removeItem('vocabmaster_token');
      updateAuthUI();
      showAuth();
    }

    function showAuth() {
      document.getElementById('authView').classList.remove('hidden');
      document.getElementById('dashboardView').classList.add('hidden');
      document.getElementById('studyView').classList.add('hidden');
    }

    function showDashboard() {
      if (!authToken) return showAuth();
      document.getElementById('authView').classList.add('hidden');
      document.getElementById('dashboardView').classList.remove('hidden');
      document.getElementById('studyView').classList.add('hidden');
      loadDashboard();
    }

    async function loadDashboard() {
      document.getElementById('authView').classList.add('hidden');
      document.getElementById('dashboardView').classList.remove('hidden');
      document.getElementById('studyView').classList.add('hidden');

      // 1. Fetch stats
      const stats = await apiRequest('/api/stats');
      document.getElementById('statTotalDecks').textContent = stats.total_decks;
      document.getElementById('statTotalCards').textContent = stats.total_cards;
      document.getElementById('statDueCards').textContent = stats.due_reviews_today;
      document.getElementById('statNewCards').textContent = stats.new_cards_ready;

      // 2. Check for active / recoverable session
      const activeRes = await apiRequest('/api/sessions/active');
      const activeBanner = document.getElementById('activeSessionBanner');
      if (activeRes.active && activeRes.session) {
        currentSession = activeRes.session;
        document.getElementById('activeSessionDesc').textContent = 
          `Session '${activeRes.session.title}' is currently at card ${activeRes.session.current_index + 1} of ${activeRes.session.total_cards}.`;
        activeBanner.classList.remove('hidden');
      } else {
        activeBanner.classList.add('hidden');
      }

      // 3. Fetch decks
      const decks = await apiRequest('/api/decks');
      renderDecks(decks);
    }

    function renderDecks(decks) {
      const container = document.getElementById('decksGrid');
      if (decks.length === 0) {
        container.innerHTML = `
          <div class="col-span-full py-12 text-center bg-slate-900 border border-slate-800 rounded-2xl p-6">
            <i class="fa-solid fa-folder-open text-4xl text-slate-600 mb-3"></i>
            <h3 class="text-base font-semibold text-white mb-1">No Decks Yet</h3>
            <p class="text-xs text-slate-400 mb-4">Create your first vocabulary deck or import a CSV/XLSX file.</p>
            <button onclick="openCreateDeckModal()" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold">Create Deck</button>
          </div>
        `;
        return;
      }

      container.innerHTML = decks.map(d => `
        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 hover:border-slate-700 transition flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between mb-2">
              <span class="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 uppercase">${d.target_language}</span>
              <button onclick="deleteDeck('${d.id}')" title="Delete Deck" class="text-slate-500 hover:text-rose-400 text-xs transition"><i class="fa-solid fa-trash-can"></i></button>
            </div>
            <h3 class="text-base font-bold text-white mb-1">${escapeHtml(d.name)}</h3>
            <p class="text-xs text-slate-400 line-clamp-2 mb-4">${escapeHtml(d.description || 'No description provided')}</p>
          </div>

          <div>
            <div class="flex items-center justify-between text-xs py-2 border-t border-slate-800/80 mb-3 text-slate-400">
              <span>Cards: <strong class="text-white">${d.total_cards || 0}</strong></span>
              <span>Due: <strong class="text-amber-400">${d.due_reviews || 0}</strong></span>
              <span>New: <strong class="text-emerald-400">${d.new_cards || 0}</strong></span>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <button onclick="startDeckSession('${d.id}')" class="py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold shadow-sm transition flex items-center justify-center gap-1.5">
                <i class="fa-solid fa-play text-[10px]"></i> Study
              </button>
              <button onclick="openImportModal('${d.id}')" class="py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg text-xs font-medium transition flex items-center justify-center gap-1.5">
                <i class="fa-solid fa-file-import text-[10px]"></i> Import
              </button>
            </div>
          </div>
        </div>
      `).join('');
    }

    // Modal controls
    function openCreateDeckModal() { document.getElementById('createDeckModal').classList.remove('hidden'); }
    function closeCreateDeckModal() { document.getElementById('createDeckModal').classList.add('hidden'); }
    function openImportModal(deckId) {
      document.getElementById('importDeckId').value = deckId;
      document.getElementById('importResultBox').classList.add('hidden');
      document.getElementById('importModal').classList.remove('hidden');
    }
    function closeImportModal() { document.getElementById('importModal').classList.add('hidden'); }

    async function handleCreateDeck(e) {
      e.preventDefault();
      const name = document.getElementById('newDeckName').value.trim();
      const target_language = document.getElementById('newDeckLang').value;
      const description = document.getElementById('newDeckDesc').value.trim();

      await apiRequest('/api/decks', {
        method: 'POST',
        body: JSON.stringify({ name, target_language, description })
      });

      closeCreateDeckModal();
      document.getElementById('newDeckName').value = '';
      document.getElementById('newDeckDesc').value = '';
      loadDashboard();
    }

    async function deleteDeck(deckId) {
      if (!confirm('Are you sure you want to delete this deck? All words and review stats will be permanently removed.')) return;
      await apiRequest(`/api/decks/${deckId}`, { method: 'DELETE' });
      loadDashboard();
    }

    async function handleImportSubmit(e) {
      e.preventDefault();
      const deckId = document.getElementById('importDeckId').value;
      const fileInput = document.getElementById('importFileInput');
      const dedup = document.getElementById('importDedupStrategy').value;
      const resultBox = document.getElementById('importResultBox');

      if (!fileInput.files.length) return;
      const file = fileInput.files[0];

      const formData = new FormData();
      formData.append('file', file);

      try {
        resultBox.innerHTML = '<span class="text-amber-400"><i class="fa-solid fa-spinner fa-spin mr-1"></i> Importing...</span>';
        resultBox.classList.remove('hidden');

        const res = await apiRequest(`/api/decks/${deckId}/import?dedup_strategy=${dedup}`, {
          method: 'POST',
          body: formData,
          isFormData: true
        });

        resultBox.className = 'p-3 rounded-lg text-xs bg-emerald-500/10 border border-emerald-500/20 text-emerald-300';
        resultBox.innerHTML = `
          <strong>Import Complete!</strong><br>
          • Total Rows: ${res.total_rows}<br>
          • Successfully Imported: ${res.imported_count}<br>
          • Skipped: ${res.skipped_count}<br>
          • Errors: ${res.error_count}
        `;
        setTimeout(() => {
          closeImportModal();
          loadDashboard();
        }, 1500);
      } catch (err) {
        resultBox.className = 'p-3 rounded-lg text-xs bg-rose-500/10 border border-rose-500/20 text-rose-300';
        resultBox.textContent = `Error: ${err.message}`;
      }
    }

    function downloadSampleCSV() {
      const csv = `term,definition,ipa,part_of_speech,examples,tags
resilience,the capacity to recover quickly from difficulties,/rɪˈzɪl.jəns/,noun,She showed great resilience during the crisis.,psychology
epiphany,a moment of sudden and great revelation,/ɪˈpɪf.ən.i/,noun,He had an epiphany that changed his entire approach.,mindset
serendipity,finding valuable things not sought for,/ˌser.ənˈdɪp.ə.ti/,noun,Finding this book was pure serendipity.,literature`;
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'sample_vocabulary.csv';
      a.click();
      URL.revokeObjectURL(url);
    }

    // STUDY SESSION ENGINE
    async function startDailyGlobalSession() {
      const res = await apiRequest('/api/sessions/start', {
        method: 'POST',
        body: JSON.stringify({})
      });
      launchSession(res);
    }

    async function startDeckSession(deckId) {
      const res = await apiRequest('/api/sessions/start', {
        method: 'POST',
        body: JSON.stringify({ deck_id: deckId })
      });
      launchSession(res);
    }

    async function resumeActiveSession() {
      if (!currentSession) return;
      const res = await apiRequest('/api/sessions/active');
      launchSession({ session: res.session, current_card: res.current_card });
    }

    function launchSession(sessionData) {
      currentSession = sessionData.session;
      currentCard = sessionData.current_card;

      if (!currentCard || currentSession.status === 'COMPLETED') {
        alert('All caught up! No cards are due for study right now.');
        return;
      }

      document.getElementById('dashboardView').classList.add('hidden');
      document.getElementById('studyView').classList.remove('hidden');
      renderCard(currentCard);
    }

    function renderCard(card) {
      currentCard = card;
      cardFlipped = false;
      cardStartTime = Date.now();

      // Update progress
      const currentIdx = card.current_index + 1;
      const total = card.total_cards;
      const pct = Math.round((currentIdx / total) * 100);

      document.getElementById('sessionDeckTitle').textContent = currentSession.title;
      document.getElementById('sessionProgressText').textContent = `Card ${currentIdx} of ${total}`;
      document.getElementById('sessionProgressBar').style.width = `${pct}%`;

      // Word details
      document.getElementById('cardLangBadge').textContent = card.language.toUpperCase();
      document.getElementById('cardStateBadge').textContent = card.state;
      document.getElementById('cardTerm').textContent = card.term;
      document.getElementById('cardIpa').textContent = card.ipa ? card.ipa : '';

      // Language specific reading (Furigana / Romaji)
      const readingEl = document.getElementById('cardReading');
      const langFields = card.language_specific_fields || {};
      if (langFields.reading) {
        readingEl.textContent = langFields.reading;
        readingEl.classList.remove('hidden');
      } else {
        readingEl.classList.add('hidden');
      }

      // Language tags
      const badgesContainer = document.getElementById('cardLangFields');
      badgesContainer.innerHTML = '';
      if (langFields.article) badgesContainer.innerHTML += `<span class="px-2 py-0.5 rounded text-xs bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 font-semibold">${langFields.article}</span>`;
      if (langFields.gender) badgesContainer.innerHTML += `<span class="px-2 py-0.5 rounded text-xs bg-sky-500/20 text-sky-300 border border-sky-500/30">${langFields.gender}</span>`;
      if (langFields.jlpt_level) badgesContainer.innerHTML += `<span class="px-2 py-0.5 rounded text-xs bg-red-500/20 text-red-300 border border-red-500/30 font-semibold">JLPT ${langFields.jlpt_level}</span>`;
      if (langFields.cefr_level) badgesContainer.innerHTML += `<span class="px-2 py-0.5 rounded text-xs bg-purple-500/20 text-purple-300 border border-purple-500/30 font-semibold">CEFR ${langFields.cefr_level}</span>`;
      if (langFields.tone) badgesContainer.innerHTML += `<span class="px-2 py-0.5 rounded text-xs bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">Thanh ${langFields.tone}</span>`;

      // Answer Details (Hidden)
      document.getElementById('answerSection').classList.add('hidden');
      document.getElementById('revealBtnContainer').classList.remove('hidden');
      document.getElementById('cardDefinition').textContent = card.definition;
      document.getElementById('cardPos').textContent = card.part_of_speech || 'word';

      const examplesBox = document.getElementById('cardExamplesBox');
      const examplesList = document.getElementById('cardExamplesList');
      if (card.examples && card.examples.length > 0) {
        examplesList.innerHTML = card.examples.map(ex => `<li>${escapeHtml(ex)}</li>`).join('');
        examplesBox.classList.remove('hidden');
      } else {
        examplesBox.classList.add('hidden');
      }
    }

    function revealAnswer() {
      cardFlipped = true;
      document.getElementById('answerSection').classList.remove('hidden');
      document.getElementById('revealBtnContainer').classList.add('hidden');
    }

    async function rateCard(rating) {
      if (!currentCard) return;
      const elapsedSeconds = ((Date.now() - cardStartTime) / 1000).toFixed(1);

      try {
        const res = await apiRequest(`/api/sessions/${currentSession.id}/answer`, {
          method: 'POST',
          body: JSON.stringify({
            rating: rating,
            time_spent_seconds: parseFloat(elapsedSeconds),
            requeue_failed_cards: true
          })
        });

        currentSession = res.session;

        if (res.is_completed || !res.next_card) {
          showSessionSummary();
        } else {
          renderCard(res.next_card);
        }
      } catch (err) {
        alert('Error recording review: ' + err.message);
      }
    }

    async function pauseStudySession() {
      if (!currentSession) return;
      await apiRequest(`/api/sessions/${currentSession.id}/pause`, { method: 'POST' });
      showDashboard();
    }

    async function abandonStudySession() {
      if (!confirm('Are you sure you want to stop this study session?')) return;
      if (currentSession) {
        await apiRequest(`/api/sessions/${currentSession.id}/abandon`, { method: 'POST' });
      }
      showDashboard();
    }

    async function showSessionSummary() {
      const summary = await apiRequest(`/api/sessions/${currentSession.id}/summary`);
      document.getElementById('summaryCardsCount').textContent = summary.completed_cards;
      document.getElementById('summaryAccuracy').textContent = `${summary.accuracy_percentage}%`;
      document.getElementById('summaryModal').classList.remove('hidden');
    }

    function closeSummaryModal() {
      document.getElementById('summaryModal').classList.add('hidden');
      showDashboard();
    }

    function speakCurrentWord() {
      if (!currentCard) return;
      const text = currentCard.term;
      const lang = currentCard.language || 'en';
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = lang === 'ja' ? 'ja-JP' : (lang === 'de' ? 'de-DE' : (lang === 'vi' ? 'vi-VN' : 'en-US'));
        window.speechSynthesis.speak(utterance);
      }
    }

    function escapeHtml(str) {
      if (!str) return '';
      return String(str).replace(/[&<>"']/g, m => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m]));
    }
  </script>
</body>
</html>
"""

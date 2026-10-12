"""Built-in Interactive Web UI for VocabMaster.
Full-featured SPA supporting all 10 core navigation views:
1. Dashboard (Tổng quan)
2. My Learning Paths (Lộ trình học)
3. Vocabulary Library (Thư viện từ vựng)
4. Flashcards (Thẻ ghi nhớ)
5. Daily Learning (Học hàng ngày - 20min 4-phase structured session)
6. Review Center (Trung tâm ôn tập)
7. Practice (Luyện tập - Viết câu & Phát âm)
8. Import Vocabulary (Nhập từ vựng - Wizard tải tệp & dán bảng)
9. Progress (Tiến độ & Chuỗi học tập)
10. Settings (Cài đặt)
"""

HTML_CONTENT = """<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>VocabMaster — Hệ Thống Học Từ Vựng Thông Minh</title>
  
  <!-- Google Fonts: Josefin Sans (Headings) & Nunito (Body) from Burnout Web -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Josefin+Sans:ital,wght@0,300;0,400;0,600;0,700;1,400;1,600&family=Nunito:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400;1,600&display=swap" rel="stylesheet">
  
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  <script>
    tailwind.config = {
      theme: {
        extend: {
          fontFamily: {
            heading: ['"Josefin Sans"', 'sans-serif'],
            sans: ['"Nunito"', 'sans-serif']
          },
          colors: {
            brand: {
              50: '#ecfdf5',
              100: '#d1fae5',
              200: '#a7f3d0',
              300: '#6ee7b7',
              400: '#34d399',
              500: '#10b981',
              600: '#059669',
              700: '#047857',
              800: '#065f46',
              900: '#064e3b'
            }
          }
        }
      }
    }
  </script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Josefin+Sans:ital,wght@0,300;0,400;0,600;0,700;1,400;1,600&family=Nunito:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400;1,600&display=swap');

    :root {
      --font-heading: 'Josefin Sans', sans-serif;
      --font-body: 'Nunito', sans-serif;
      --primary: #059669;
      --primary-light: #34d399;
      --primary-dark: #047857;
      --accent: #0284c7;
      --accent-warm: #f59e0b;
      --streak-fire: #f97316;
      --bg-gradient: linear-gradient(135deg, #f0fdf4 0%, #ecfeff 40%, #fefce8 100%);
      --card-bg: rgba(255, 255, 255, 0.92);
      --card-border: rgba(255, 255, 255, 0.85);
      --text-main: #1e293b;
      --text-muted: #64748b;
    }

    * {
      box-sizing: border-box;
    }

    body {
      font-family: var(--font-body) !important;
      color: var(--text-main) !important;
      background: var(--bg-gradient) !important;
      background-attachment: fixed !important;
      min-height: 100vh;
    }

    h1, h2, h3, h4, h5, h6, .font-heading {
      font-family: var(--font-heading) !important;
      color: #0f172a !important;
    }

    /* Glassmorphism Header & Navigation from Burnout Web */
    header {
      background: rgba(255, 255, 255, 0.94) !important;
      backdrop-filter: blur(16px) !important;
      -webkit-backdrop-filter: blur(16px) !important;
      border-bottom: 1px solid rgba(226, 232, 240, 0.85) !important;
      box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.03) !important;
    }

    aside#appSidebar {
      background: rgba(255, 255, 255, 0.85) !important;
      backdrop-filter: blur(16px) !important;
      -webkit-backdrop-filter: blur(16px) !important;
      border-right: 1px solid rgba(226, 232, 240, 0.85) !important;
      box-shadow: 4px 0 20px -2px rgba(15, 23, 42, 0.02) !important;
    }

    /* Glassmorphism Cards & Panels from Burnout Web */
    .bg-slate-900,
    .bg-slate-900\/90,
    .bg-slate-900\/80,
    .bg-slate-900\/70,
    .bg-slate-900\/60,
    .bg-slate-900\/40,
    .bg-slate-950,
    .bg-slate-950\/90,
    .bg-slate-950\/80,
    .bg-slate-800,
    .bg-slate-800\/90,
    .bg-slate-800\/80,
    .bg-slate-800\/60,
    .bg-slate-800\/50,
    .bg-slate-800\/40 {
      background: rgba(255, 255, 255, 0.92) !important;
      backdrop-filter: blur(16px) !important;
      -webkit-backdrop-filter: blur(16px) !important;
      border-color: rgba(226, 232, 240, 0.85) !important;
      color: #1e293b !important;
      box-shadow: 0 10px 30px rgba(15, 23, 42, 0.04) !important;
    }

    /* Borders */
    .border-slate-800,
    .border-slate-800\/80,
    .border-slate-800\/60,
    .border-slate-700,
    .border-slate-700\/80,
    .border-slate-700\/60,
    .border-slate-700\/50 {
      border-color: #e2e8f0 !important;
    }

    /* Typography Colors */
    .text-white {
      color: #0f172a !important;
    }

    .text-slate-400,
    .text-slate-500 {
      color: #64748b !important;
    }

    .text-slate-300,
    .text-slate-200,
    .text-slate-100 {
      color: #334155 !important;
    }

    /* Keep white text on primary buttons, badges, gradients */
    button.bg-emerald-600,
    button.bg-emerald-500,
    button.bg-brand-600,
    button.bg-brand-500,
    button.bg-indigo-600,
    button.bg-rose-600,
    button.bg-blue-600,
    button[type="submit"],
    .bg-gradient-to-tr,
    .bg-gradient-to-r {
      color: #ffffff !important;
    }

    button.bg-emerald-600 *,
    button.bg-emerald-500 *,
    button.bg-brand-600 *,
    button.bg-brand-500 *,
    button[type="submit"] *,
    .bg-gradient-to-tr *,
    .bg-gradient-to-r * {
      color: #ffffff !important;
    }

    /* Navigation item active state */
    .nav-item.bg-emerald-500\/10 {
      background: #ecfdf5 !important;
      color: #059669 !important;
      font-weight: 700 !important;
      border-left: 3px solid #059669 !important;
      box-shadow: 0 2px 8px rgba(5, 150, 105, 0.08) !important;
    }

    .nav-item:hover:not(.bg-emerald-500\/10) {
      background: rgba(241, 245, 249, 0.8) !important;
      color: #0f172a !important;
    }

    /* Form Inputs, Selects, Textareas */
    input:not([type="checkbox"]):not([type="radio"]),
    select,
    textarea {
      background: #ffffff !important;
      border: 1px solid #cbd5e1 !important;
      color: #0f172a !important;
      border-radius: 0.75rem !important;
    }

    input:focus, select:focus, textarea:focus {
      border-color: #059669 !important;
      box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.15) !important;
      outline: none !important;
    }

    /* Burnout Theme Custom Scrollbar */
    ::-webkit-scrollbar {
      width: 8px;
      height: 8px;
    }
    ::-webkit-scrollbar-track {
      background: #f1f5f9;
    }
    ::-webkit-scrollbar-thumb {
      background: #a7f3d0;
      border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: #34d399;
    }

    /* Modals */
    .fixed.inset-0.bg-slate-950\/90,
    .fixed.inset-0.bg-slate-950\/80 {
      background: rgba(15, 23, 42, 0.45) !important;
      backdrop-filter: blur(14px) !important;
      -webkit-backdrop-filter: blur(14px) !important;
    }

    .font-cjk { font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "WenQuanYi Micro Hei", sans-serif; }
  </style>
</head>
<body class="bg-gradient-to-br from-emerald-50 via-teal-50 to-amber-50 min-h-screen text-slate-800 antialiased selection:bg-emerald-200 selection:text-emerald-900 font-sans flex flex-col">

  <!-- Top Navigation Header -->
  <header class="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-40">
    <div class="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
      <!-- Logo & Brand with Mobile Menu Toggle Button -->
      <div class="flex items-center space-x-2.5">
        <!-- Mobile Sidebar Hamburger Toggle Button -->
        <button id="btnToggleMobileSidebar" onclick="toggleMobileSidebar()" class="md:hidden p-2 rounded-xl text-slate-300 hover:text-white hover:bg-slate-800 transition focus:outline-none flex items-center justify-center border border-slate-700/80 shadow-sm" title="Mở danh mục menu học tập">
          <i class="fa-solid fa-bars text-base"></i>
        </button>

        <div class="flex items-center space-x-2.5 cursor-pointer" onclick="navigateTo('dashboard')">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-emerald-400 flex items-center justify-center text-white shadow-lg shadow-brand-500/20">
            <i class="fa-solid fa-graduation-cap text-lg"></i>
          </div>
          <div>
            <span class="text-xl font-black tracking-tight bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 bg-clip-text text-transparent">VocabMaster</span>
            <span class="text-[10px] px-2 py-0.5 ml-1.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 font-bold uppercase tracking-wider">SM-2+ v2.0</span>
          </div>
        </div>
      </div>

      <!-- Header Center: Quick Language Switcher & Active Path -->
      <div id="headerStudyContext" class="hidden md:flex items-center gap-3">
        <!-- Active Workspace Badge -->
        <div id="headerWorkspaceBadge" class="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 shadow-sm">
          <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span class="font-bold text-emerald-700">🇬🇧 English Mode</span>
        </div>

        <!-- Learning Language Dropdown -->
        <div class="relative">
          <select id="headerLangSelect" onchange="switchLearningLanguage(this.value)" class="bg-slate-800 hover:bg-slate-700/80 border border-slate-700 text-xs text-slate-200 font-medium rounded-lg px-3 py-1.5 focus:outline-none focus:border-brand-500 transition cursor-pointer">
            <option value="en">🇬🇧 Chuyển sang: Tiếng Anh (English Mode)</option>
            <option value="zh">🇨🇳 Chuyển sang: Tiếng Trung (Chinese Mode)</option>
          </select>
        </div>

        <!-- Active Path Badge -->
        <div id="headerActivePathBadge" class="hidden items-center gap-1.5 px-3 py-1 rounded-lg bg-teal-500/10 border border-teal-500/20 text-xs text-teal-300">
          <i class="fa-solid fa-route text-[10px]"></i>
          <span id="headerPathName" class="font-medium max-w-[140px] truncate">Lộ trình TOEIC</span>
        </div>
      </div>

      <!-- Header Right: Auth & Controls -->
      <div class="flex items-center space-x-3">
        <a href="/docs" target="_blank" class="hidden sm:flex px-2.5 py-1 text-xs font-medium text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-lg transition border border-slate-700 items-center gap-1.5">
          <i class="fa-solid fa-code"></i> API
        </a>
        <div id="authControls" class="flex items-center space-x-2">
          <!-- Auth buttons dynamically rendered -->
        </div>
      </div>
    </div>
  </header>

  <!-- Mobile Sidebar Backdrop Overlay -->
  <div id="sidebarBackdrop" onclick="closeMobileSidebar()" class="fixed inset-0 z-40 bg-slate-950/80 backdrop-blur-sm hidden md:hidden transition-opacity duration-300"></div>

  <!-- App Body Layout (Sidebar + Main View) -->
  <div class="flex-1 max-w-7xl w-full mx-auto flex flex-col md:flex-row">
    
    <!-- Left Navigation Sidebar (Responsive Mobile Drawer + Desktop Static) -->
    <aside id="appSidebar" class="fixed inset-y-0 left-0 z-50 w-72 max-w-[85vw] bg-slate-900 border-r border-slate-800 p-4 space-y-5 overflow-y-auto flex flex-col transform -translate-x-full transition-transform duration-300 ease-in-out shadow-2xl md:translate-x-0 md:static md:w-64 md:flex md:flex-col md:bg-slate-900/40 md:border-r md:border-slate-800/80 md:shadow-none shrink-0">
      
      <!-- Mobile Drawer Header (close button & brand) -->
      <div class="flex items-center justify-between pb-3 border-b border-slate-800 md:hidden">
        <div class="flex items-center space-x-2">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-tr from-brand-600 to-emerald-400 flex items-center justify-center text-white shadow-md">
            <i class="fa-solid fa-graduation-cap text-sm"></i>
          </div>
          <div>
            <span class="text-sm font-black tracking-tight text-white">VocabMaster</span>
            <span class="text-[9px] px-1.5 py-0.5 ml-1 rounded-full bg-emerald-900/60 text-emerald-300 border border-emerald-700 font-bold uppercase">Menu</span>
          </div>
        </div>
        <button onclick="closeMobileSidebar()" class="w-8 h-8 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 flex items-center justify-center border border-slate-700/60 transition" title="Đóng menu">
          <i class="fa-solid fa-xmark text-sm"></i>
        </button>
      </div>

      <!-- Mobile Quick Language Switcher inside Drawer -->
      <div class="md:hidden pb-3 border-b border-slate-800 space-y-1.5">
        <div class="text-[10px] font-bold text-slate-500 uppercase tracking-wider px-1">Chế Độ Ngôn Ngữ</div>
        <select id="mobileLangSelect" onchange="switchLearningLanguage(this.value); closeMobileSidebar();" class="w-full bg-slate-800 border border-slate-700 text-xs text-slate-200 font-medium rounded-lg px-3 py-2 focus:outline-none focus:border-brand-500 transition">
          <option value="en">🇬🇧 Tiếng Anh (English Mode)</option>
          <option value="zh">🇨🇳 Tiếng Trung (Chinese Mode)</option>
        </select>
      </div>

      <div class="space-y-1">
        <div class="text-[10px] font-bold text-slate-500 uppercase tracking-wider px-3 mb-2">Học Tập & Ôn Luyện</div>
        <button onclick="navigateTo('dashboard')" id="nav-dashboard" class="nav-item w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold text-emerald-400 bg-emerald-500/10 transition">
          <i class="fa-solid fa-house w-4 text-center"></i> <span>Tổng Quan</span>
        </button>
        <button onclick="navigateTo('paths')" id="nav-paths" class="nav-item w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800/60 transition">
          <i class="fa-solid fa-route w-4 text-center"></i> <span>Lộ Trình Học</span>
        </button>
        <button onclick="navigateTo('vocab')" id="nav-vocab" class="nav-item w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800/60 transition">
          <i class="fa-solid fa-book-bookmark w-4 text-center"></i> <span>Thư Viện Từ Vựng</span>
        </button>
        <button onclick="navigateTo('flashcards')" id="nav-flashcards" class="nav-item w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800/60 transition">
          <i class="fa-solid fa-layer-group w-4 text-center"></i> <span>Thẻ Ghi Nhớ</span>
        </button>
      </div>

      <div class="space-y-1">
        <div class="text-[10px] font-bold text-slate-500 uppercase tracking-wider px-3 mb-2">Phiên Học Hàng Ngày</div>
        <button onclick="startDailyStructuredSession()" id="nav-daily" class="nav-item w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800/60 transition">
          <i class="fa-solid fa-clock-rotate-left w-4 text-center text-amber-400"></i> <span>Học 20 Phút Mỗi Ngày</span>
        </button>
        <button onclick="navigateTo('reviews')" id="nav-reviews" class="nav-item w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800/60 transition">
          <i class="fa-solid fa-arrows-rotate w-4 text-center text-rose-400"></i> <span>Trung Tâm Ôn Tập</span>
        </button>
        <button onclick="navigateTo('practice')" id="nav-practice" class="nav-item w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800/60 transition">
          <i class="fa-solid fa-pen-fancy w-4 text-center text-cyan-400"></i> <span>Luyện Viết & Nói</span>
        </button>
      </div>

      <div class="space-y-1">
        <div class="text-[10px] font-bold text-slate-500 uppercase tracking-wider px-3 mb-2">Quản Lý & Cài Đặt</div>
        <button onclick="navigateTo('importer')" id="nav-importer" class="nav-item w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800/60 transition">
          <i class="fa-solid fa-file-import w-4 text-center text-indigo-400"></i> <span>Nhập Từ Vựng</span>
        </button>
        <button onclick="navigateTo('progress')" id="nav-progress" class="nav-item w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800/60 transition">
          <i class="fa-solid fa-chart-line w-4 text-center text-emerald-400"></i> <span>Tiến Độ & Chuỗi Học</span>
        </button>
        <button onclick="navigateTo('settings')" id="nav-settings" class="nav-item w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800/60 transition">
          <i class="fa-solid fa-gear w-4 text-center"></i> <span>Cài Đặt</span>
        </button>
      </div>

      <!-- Streak Mini Widget -->
      <div class="mt-auto pt-4 border-t border-slate-800">
        <div class="bg-slate-800/60 rounded-xl p-3 border border-slate-800 flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="text-xl">🔥</span>
            <div>
              <div class="text-[11px] font-bold text-white"><span id="sidebarStreakCount">0</span> ngày liên tiếp</div>
              <div class="text-[9px] text-slate-400">Duy trì thói quen học</div>
            </div>
          </div>
          <span id="sidebarStreakBadge" class="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 font-bold border border-amber-500/20">Hoạt động</span>
        </div>
      </div>
    </aside>

    <!-- Main Dynamic Content Workspace -->
    <main class="flex-1 p-4 sm:p-6 lg:p-8 overflow-y-auto scrollbar-thin">
      
      <!-- VIEW: AUTHENTICATION -->
      <div id="view-auth" class="max-w-md mx-auto my-12 bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-2xl">
        <div class="text-center mb-6">
          <div class="w-12 h-12 rounded-2xl bg-emerald-500/20 text-emerald-400 mx-auto flex items-center justify-center text-xl mb-3 shadow-inner">
            <i class="fa-solid fa-graduation-cap"></i>
          </div>
          <h2 id="authTitle" class="text-2xl font-bold text-white mb-1">Chào Mừng Đến VocabMaster</h2>
          <p class="text-xs text-slate-400">Ứng dụng học từ vựng khoa học dựa trên Lặp lại Ngắt quãng (Spaced Repetition)</p>
        </div>

        <div class="flex border-b border-slate-800 mb-6">
          <button id="tabLogin" onclick="switchAuthTab('login')" class="flex-1 pb-3 text-xs font-bold border-b-2 border-emerald-500 text-emerald-400 transition">Đăng Nhập</button>
          <button id="tabRegister" onclick="switchAuthTab('register')" class="flex-1 pb-3 text-xs font-bold border-b-2 border-transparent text-slate-400 hover:text-slate-200 transition">Đăng Ký</button>
        </div>

        <form id="authForm" onsubmit="handleAuthSubmit(event)" class="space-y-4">
          <div id="usernameGroup" class="hidden">
            <label class="block text-xs font-semibold text-slate-300 mb-1">Tên Người Dùng</label>
            <input type="text" id="authUsername" class="w-full px-3.5 py-2.5 rounded-lg bg-slate-800 border border-slate-700 text-white text-xs focus:outline-none focus:border-brand-500" placeholder="nguyenvana">
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1">Email hoặc Tên Đăng Nhập</label>
            <input type="text" id="authEmail" required class="w-full px-3.5 py-2.5 rounded-lg bg-slate-800 border border-slate-700 text-white text-xs focus:outline-none focus:border-brand-500" placeholder="admin hoặc admin@vocabmaster.app">
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1">Mật Khẩu</label>
            <input type="password" id="authPassword" required class="w-full px-3.5 py-2.5 rounded-lg bg-slate-800 border border-slate-700 text-white text-xs focus:outline-none focus:border-brand-500" placeholder="••••••••">
          </div>
          <div id="authError" class="text-xs text-rose-400 hidden p-2 bg-rose-500/10 rounded border border-rose-500/20"></div>
          <button type="submit" id="authSubmitBtn" class="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-bold text-xs transition shadow-lg shadow-emerald-600/30">
            Đăng Nhập
          </button>
        </form>

        <div class="mt-6 pt-6 border-t border-slate-800 text-center">
          <button onclick="quickDemoLogin()" class="w-full py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white rounded-lg text-xs font-medium border border-slate-700 transition flex items-center justify-center gap-2">
            <i class="fa-solid fa-bolt text-amber-400"></i> Đăng nhập dùng thử 1 chạm (Demo)
          </button>
        </div>
      </div>

      <!-- VIEW 1: DASHBOARD -->
      <div id="view-dashboard" class="hidden space-y-6">
        <!-- Top banner -->
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 class="text-2xl font-black text-white flex items-center gap-2">
              <span>Bảng Tổng Quan Học Tập</span>
            </h1>
            <p class="text-xs text-slate-400">Kế hoạch học tập hàng ngày và tiến độ củng cố trí nhớ dài hạn</p>
          </div>
          <div class="flex flex-wrap items-center gap-2">
            <button onclick="startDailyStructuredSession()" class="px-4 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold shadow-lg shadow-emerald-600/30 transition flex items-center gap-2">
              <i class="fa-solid fa-play"></i> Học 20 Phút
            </button>
            <button onclick="startDailyStructuredSession(true)" title="Ôn tập tự do không bị giới hạn số thẻ mỗi ngày" class="px-3.5 py-2.5 bg-gradient-to-r from-teal-600 to-emerald-600 hover:from-teal-500 hover:to-emerald-500 text-white rounded-xl text-xs font-bold shadow-lg shadow-teal-600/20 transition flex items-center gap-1.5">
              <i class="fa-solid fa-infinity"></i> Ôn Tập Không Giới Hạn
            </button>
            <button onclick="seedSampleTemplateDeck()" title="Tạo 1 bộ từ vựng mẫu có sẵn từ vựng tiêu chuẩn" class="px-3.5 py-2.5 bg-amber-600/20 hover:bg-amber-600/30 text-amber-300 border border-amber-500/30 rounded-xl text-xs font-bold transition flex items-center gap-1.5 shadow">
              <i class="fa-solid fa-wand-magic-sparkles text-amber-400"></i> Thêm Bộ Thẻ Mẫu
            </button>
            <button onclick="openCreateVocabModal()" class="px-3.5 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-xl text-xs font-semibold transition flex items-center gap-1.5">
              <i class="fa-solid fa-plus-circle text-emerald-400"></i> Thêm Từ Thủ Công
            </button>
            <button onclick="openCreateDeckModal()" class="px-3.5 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-xl text-xs font-semibold transition flex items-center gap-1.5">
              <i class="fa-solid fa-folder-plus text-cyan-400"></i> Tạo Bộ Thẻ
            </button>
          </div>
        </div>

        <!-- 4 Key Metrics Cards -->
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="bg-slate-900 border border-slate-800 rounded-2xl p-4">
            <div class="text-[11px] text-slate-400 font-medium mb-1">🔥 Chuỗi Học Tập</div>
            <div id="dashStreak" class="text-2xl font-black text-amber-400">0 ngày</div>
            <div class="text-[10px] text-slate-500 mt-1">Kỷ lục: <span id="dashLongestStreak">0</span> ngày</div>
          </div>
          <div class="bg-slate-900 border border-slate-800 rounded-2xl p-4">
            <div class="text-[11px] text-slate-400 font-medium mb-1">📚 Tổng Số Từ Vựng</div>
            <div id="dashTotalWords" class="text-2xl font-black text-teal-400">0</div>
            <div class="text-[10px] text-slate-500 mt-1">Trong <span id="dashTotalDecks">0</span> bộ từ vựng</div>
          </div>
          <div class="bg-slate-900 border border-slate-800 rounded-2xl p-4">
            <div class="text-[11px] text-slate-400 font-medium mb-1">⏰ Thẻ Cần Ôn Hôm Nay</div>
            <div id="dashDueCards" class="text-2xl font-black text-rose-400">0</div>
            <div class="text-[10px] text-slate-500 mt-1">Thuật toán SM-2+ đã lên lịch</div>
          </div>
          <div class="bg-slate-900 border border-slate-800 rounded-2xl p-4">
            <div class="text-[11px] text-slate-400 font-medium mb-1">✨ Từ Mới Sẵn Sàng</div>
            <div id="dashNewCards" class="text-2xl font-black text-emerald-400">0</div>
            <div class="text-[10px] text-slate-500 mt-1">Mục tiêu hôm nay: <span id="dashDailyTarget">5</span> từ</div>
          </div>
        </div>

        <!-- Active Recoverable Session Banner -->
        <div id="activeSessionBanner" class="hidden bg-gradient-to-r from-amber-950/40 via-amber-900/20 to-slate-900 border border-amber-500/30 rounded-2xl p-4 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center text-lg">
              <i class="fa-solid fa-rotate-left"></i>
            </div>
            <div>
              <div class="font-bold text-amber-200 text-sm">Tìm Thấy Phiên Học Chưa Hoàn Thành!</div>
              <div id="activeSessionDesc" class="text-xs text-amber-300/70">Phiên học trước đã được lưu tự động. Bạn có thể tiếp tục ngay lập tức.</div>
            </div>
          </div>
          <button onclick="resumeActiveSession()" class="px-4 py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-lg text-xs transition">
            Tiếp Tục Học
          </button>
        </div>

        <!-- Recent Decks Section -->
        <div>
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-base font-bold text-white">Các Bộ Từ Vựng Của Bạn</h3>
            <button onclick="navigateTo('importer')" class="text-xs text-emerald-400 hover:underline flex items-center gap-1">
              <i class="fa-solid fa-file-import"></i> Nhập từ vựng mới
            </button>
          </div>
          <div id="dashDecksGrid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <!-- Rendered by JS -->
          </div>
        </div>
      </div>

      <!-- VIEW 2: MY LEARNING PATHS -->
      <div id="view-paths" class="hidden space-y-6">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 class="text-2xl font-black text-white">Lộ Trình Học Tập</h1>
            <p class="text-xs text-slate-400">Tổ chức việc học theo các mục tiêu chuyên biệt (TOEIC, HSK, Giao tiếp,...)</p>
          </div>
          <button onclick="openCreatePathModal()" class="px-4 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold transition flex items-center gap-2">
            <i class="fa-solid fa-plus"></i> Tạo Lộ Trình Mới
          </button>
        </div>

        <!-- Paths List -->
        <div id="pathsList" class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Rendered by JS -->
        </div>
      </div>

      <!-- VIEW 3: VOCABULARY LIBRARY -->
      <div id="view-vocab" class="hidden space-y-6">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 class="text-2xl font-black text-white">Thư Viện Từ Vựng</h1>
            <p class="text-xs text-slate-400">Tra cứu, quản lý từ vựng, mối quan hệ họ từ và phát âm</p>
          </div>
          <div class="flex items-center gap-2">
            <button onclick="openCreateVocabModal()" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold transition flex items-center gap-1.5 shadow-lg shadow-emerald-600/20">
              <i class="fa-solid fa-plus-circle"></i> Thêm Từ Mới Thủ Công
            </button>
            <button onclick="navigateTo('importer')" class="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-xl text-xs font-semibold transition flex items-center gap-1.5">
              <i class="fa-solid fa-file-import"></i> Nhập File
            </button>
          </div>
        </div>

        <!-- Search & Filter Controls -->
        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-4 flex flex-col md:flex-row gap-3 items-center">
          <div class="flex-1 w-full relative">
            <i class="fa-solid fa-magnifying-glass absolute left-3.5 top-3 text-slate-400 text-xs"></i>
            <input type="text" id="vocabSearchInput" oninput="debounceFilterVocab()" placeholder="Tìm kiếm từ, nghĩa, phát âm, tag..." class="w-full pl-9 pr-3.5 py-2 rounded-xl bg-slate-800 border border-slate-700 text-xs text-white focus:outline-none focus:border-brand-500">
          </div>
          <select id="vocabFilterDeck" onchange="filterVocabTable()" class="w-full md:w-48 px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-xs text-slate-200 focus:outline-none">
            <option value="">Tất cả bộ thẻ</option>
          </select>
          <select id="vocabFilterPos" onchange="filterVocabTable()" class="w-full md:w-36 px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-xs text-slate-200 focus:outline-none">
            <option value="">Tất cả loại từ</option>
            <option value="noun">Danh từ</option>
            <option value="verb">Động từ</option>
            <option value="adjective">Tính từ</option>
            <option value="adverb">Trạng từ</option>
          </select>
          <button id="vocabFilterFavBtn" onclick="toggleFavoriteFilter()" class="w-full md:w-auto px-3.5 py-2 rounded-xl bg-slate-800 border border-slate-700 text-xs text-slate-300 hover:text-amber-400 transition flex items-center justify-center gap-1.5">
            <i class="fa-regular fa-star"></i> Yêu thích
          </button>
        </div>

        <!-- Vocabulary Data Table -->
        <div class="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
          <div class="overflow-x-auto scrollbar-thin">
            <table class="w-full text-left text-xs">
              <thead class="bg-slate-800/60 text-slate-400 font-semibold uppercase text-[10px] tracking-wider border-b border-slate-800">
                <tr>
                  <th class="px-4 py-3">Từ vựng</th>
                  <th class="px-4 py-3">Phát âm / Pinyin</th>
                  <th class="px-4 py-3">Loại từ</th>
                  <th class="px-4 py-3">Định nghĩa & Nghĩa Tiếng Việt</th>
                  <th class="px-4 py-3">Từ gốc / Quan hệ</th>
                  <th class="px-4 py-3 text-center">Trạng thái SRS</th>
                  <th class="px-4 py-3 text-right">Thao tác</th>
                </tr>
              </thead>
              <tbody id="vocabTableBody" class="divide-y divide-slate-800/60 text-slate-300">
                <!-- Rendered by JS -->
              </tbody>
            </table>
          </div>
          <div id="vocabEmptyNotice" class="hidden p-8 text-center text-slate-500 text-xs">
            Không tìm thấy từ vựng nào khớp với bộ lọc.
          </div>
        </div>
      </div>

      <!-- VIEW 4: FLASHCARDS BROWSER -->
      <div id="view-flashcards" class="hidden space-y-6">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 class="text-2xl font-black text-white">Thẻ Ghi Nhớ (Flashcards)</h1>
            <p class="text-xs text-slate-400">Xem nhanh thẻ flashcard để kiểm tra trí nhớ trước khi bắt đầu bài học</p>
          </div>
          <div class="flex items-center gap-2">
            <select id="flashcardDeckSelector" onchange="loadDeckFlashcards(this.value)" class="px-3.5 py-2 bg-slate-800 border border-slate-700 rounded-xl text-xs text-slate-200 focus:outline-none">
              <!-- Options populated by JS -->
            </select>
            <button onclick="editCurrentFlashcardDeck()" title="Đổi tên bộ thẻ đang chọn" class="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 rounded-xl text-xs font-semibold transition flex items-center gap-1.5 shrink-0">
              <i class="fa-solid fa-pen-to-square text-emerald-400"></i> Đổi tên bộ thẻ
            </button>
          </div>
        </div>

        <div id="flashcardBrowseDeckContainer" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <!-- Rendered by JS -->
        </div>
      </div>

      <!-- VIEW 5: ACTIVE DAILY STUDY SESSION (Interactive 4-Phase SM-2+) -->
      <div id="view-daily-session" class="hidden max-w-2xl mx-auto space-y-6">
        <!-- Session Progress Card -->
        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-4">
          <div class="flex items-center justify-between text-xs mb-2">
            <div class="flex items-center gap-2">
              <span id="sessionPhaseBadge" class="px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold uppercase text-[10px]">
                Giai đoạn 1: Ôn tập nhanh
              </span>
              <span id="sessionDeckTitle" class="text-slate-400 font-medium">Phiên 20 phút</span>
            </div>
            <div class="text-slate-400 font-mono text-[11px]" id="sessionCardIndexText">Thẻ 1 / 10</div>
          </div>
          <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
            <div id="sessionProgressBar" class="bg-gradient-to-r from-emerald-500 to-teal-400 h-full transition-all duration-300" style="width: 10%"></div>
          </div>
        </div>

        <!-- Interactive Study Flashcard Box -->
        <div id="sessionCardBox" class="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl relative min-h-[420px] flex flex-col justify-between">
          <!-- Top Card Meta -->
          <div class="flex items-center justify-between mb-2">
            <span id="cardLangTag" class="px-2.5 py-1 rounded-md text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 uppercase">EN</span>
            <div class="flex items-center gap-2">
              <span id="cardSrsState" class="px-2.5 py-1 rounded-md text-[10px] font-semibold bg-slate-800 text-slate-300 border border-slate-700">NEW</span>
              <button onclick="speakCurrentWord()" title="Nghe phát âm bản ngữ (Web Speech TTS)" class="w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-emerald-400 flex items-center justify-center transition border border-slate-700">
                <i class="fa-solid fa-volume-high text-xs"></i>
              </button>
            </div>
          </div>

          <!-- Prompt & Word Section -->
          <div class="my-auto text-center py-6">
            <div id="cardExtraReading" class="text-sm font-medium text-emerald-400 mb-1 hidden"></div>
            <div id="cardMainTerm" class="text-4xl sm:text-5xl font-black text-white tracking-tight mb-2">Word</div>
            <div id="cardMainIpa" class="text-sm text-slate-400 font-mono tracking-wider">/ipa/</div>
            <div id="cardLangAttributes" class="flex flex-wrap items-center justify-center gap-2 mt-3"></div>
          </div>

          <!-- Flipped Answer Section (Revealed after click/Space) -->
          <div id="cardAnswerSection" class="hidden mt-6 pt-6 border-t border-slate-800 animate-fade-in space-y-4">
            <div class="text-center">
              <div id="cardMainPos" class="inline-block px-2.5 py-0.5 rounded text-xs font-semibold bg-teal-500/10 text-teal-300 border border-teal-500/20 mb-2">noun</div>
              <div id="cardMainMeaning" class="text-2xl font-bold text-emerald-200">Nghĩa tiếng Việt ở đây</div>
            </div>

            <!-- Root Word Relationship Alert -->
            <div id="cardRootWordBox" class="hidden bg-indigo-950/30 border border-indigo-800/40 rounded-xl p-3 text-xs text-indigo-300 flex items-center gap-2">
              <i class="fa-solid fa-code-branch text-indigo-400"></i>
              <span>Từ gốc liên quan: <strong id="cardRootWordText" class="text-white"></strong></span>
            </div>

            <!-- Examples -->
            <div id="cardExamplesBox" class="bg-slate-950/60 rounded-xl p-4 border border-slate-800/60 text-xs text-slate-300 space-y-1 text-left hidden">
              <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Ví dụ minh họa:</div>
              <ul id="cardExamplesList" class="list-disc list-inside space-y-1"></ul>
            </div>

            <!-- SM-2+ Evaluation Buttons -->
            <div>
              <div class="text-[11px] text-slate-400 text-center mb-2 font-medium">Bạn nhớ từ này ở mức độ nào? (Phím 0 đến 5)</div>
              <div class="grid grid-cols-3 sm:grid-cols-6 gap-2">
                <button onclick="submitStudyAnswer(0)" class="py-2.5 bg-rose-950/40 hover:bg-rose-900/60 border border-rose-800/50 rounded-xl text-center transition">
                  <div class="text-xs font-bold text-rose-400">0</div>
                  <div class="text-[9px] text-rose-300/70">Quên hẳn</div>
                </button>
                <button onclick="submitStudyAnswer(1)" class="py-2.5 bg-orange-950/40 hover:bg-orange-900/60 border border-orange-800/50 rounded-xl text-center transition">
                  <div class="text-xs font-bold text-orange-400">1</div>
                  <div class="text-[9px] text-orange-300/70">Không nhớ</div>
                </button>
                <button onclick="submitStudyAnswer(2)" class="py-2.5 bg-amber-950/40 hover:bg-amber-900/60 border border-amber-800/50 rounded-xl text-center transition">
                  <div class="text-xs font-bold text-amber-400">2</div>
                  <div class="text-[9px] text-amber-300/70">Khó khăn</div>
                </button>
                <button onclick="submitStudyAnswer(3)" class="py-2.5 bg-lime-950/40 hover:bg-lime-900/60 border border-lime-800/50 rounded-xl text-center transition">
                  <div class="text-xs font-bold text-lime-400">3</div>
                  <div class="text-[9px] text-lime-300/70">Nhớ tàm tạm</div>
                </button>
                <button onclick="submitStudyAnswer(4)" class="py-2.5 bg-emerald-950/40 hover:bg-emerald-900/60 border border-emerald-800/50 rounded-xl text-center transition">
                  <div class="text-xs font-bold text-emerald-400">4</div>
                  <div class="text-[9px] text-emerald-300/70">Nhớ tốt</div>
                </button>
                <button onclick="submitStudyAnswer(5)" class="py-2.5 bg-teal-950/40 hover:bg-teal-900/60 border border-teal-800/50 rounded-xl text-center transition">
                  <div class="text-xs font-bold text-teal-400">5</div>
                  <div class="text-[9px] text-teal-300/70">Rất dễ</div>
                </button>
              </div>
            </div>
          </div>

          <!-- Reveal Action (Before flip) -->
          <div id="cardRevealContainer" class="mt-8 text-center">
            <button onclick="revealStudyAnswer()" class="w-full py-3.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-bold text-sm transition shadow-lg shadow-emerald-600/30 flex items-center justify-center gap-2">
              <span>Xem Đáp Án</span>
              <kbd class="px-2 py-0.5 text-xs bg-emerald-700/60 rounded border border-emerald-500/40 font-mono">Space</kbd>
            </button>
          </div>
        </div>

        <!-- Session Controls -->
        <div class="flex items-center justify-between text-xs text-slate-400">
          <button onclick="pauseStudySession()" class="hover:text-slate-200 transition flex items-center gap-1.5">
            <i class="fa-solid fa-pause"></i> Tạm dừng phiên
          </button>
          <button onclick="abandonStudySession()" class="hover:text-rose-400 transition flex items-center gap-1.5">
            <i class="fa-solid fa-xmark"></i> Thoát phiên học
          </button>
        </div>
      </div>

      <!-- VIEW 6: REVIEW CENTER -->
      <div id="view-reviews" class="hidden space-y-6">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 class="text-2xl font-black text-white flex items-center gap-2">
              <i class="fa-solid fa-arrows-rotate text-rose-400"></i> Trung Tâm Ôn Tập & Luyện Tập
            </h1>
            <p class="text-xs text-slate-400">Ôn tập thẻ theo thuật toán SRS và thực hành đa chiều: Phiên âm, Đọc phát âm chuẩn & Viết từ vựng</p>
          </div>
          <div class="flex items-center gap-2">
            <button onclick="startQuickReviewSession()" class="px-4 py-2.5 bg-rose-600 hover:bg-rose-500 text-white rounded-xl text-xs font-bold transition flex items-center gap-2 shadow-lg shadow-rose-600/30">
              <i class="fa-solid fa-bolt"></i> Ôn Tập Thẻ SRS Ngay
            </button>
          </div>
        </div>

        <!-- Sub-Tabs Switcher: Quiz Đảo Đề vs SRS Flashcards vs SRS Relearn -->
        <div class="flex flex-wrap items-center gap-2 p-1.5 bg-slate-900/80 rounded-2xl border border-slate-800 max-w-fit">
          <button id="btnSubTabReviewExercises" onclick="switchReviewSubTab('exercises')" class="px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-2 bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shadow-sm">
            <i class="fa-solid fa-shuffle"></i> 🎯 Quiz Đảo Đề & Giấu Từng Phần (Cloze)
          </button>
          <button id="btnSubTabReviewSRS" onclick="switchReviewSubTab('srs')" class="px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-2 text-slate-400 hover:text-white hover:bg-slate-800/60 border border-transparent">
            <i class="fa-solid fa-layer-group"></i> ⚡ Thẻ Ôn Tập Flashcards SRS
          </button>
          <button id="btnSubTabReviewRelearn" onclick="switchReviewSubTab('relearn')" class="px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-2 text-slate-400 hover:text-white hover:bg-slate-800/60 border border-transparent">
            <i class="fa-solid fa-stairs text-amber-400"></i> 🪜 Lặp Lại Ngắt Quãng (SRS Re-learning)
          </button>
        </div>

        <!-- SUB-TAB 1: SRS FLASHCARDS & DUE LIST (Preserved Completely) -->
        <div id="reviewSubTabSRSContainer" class="hidden space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 text-center">
              <div class="text-3xl font-black text-rose-400 mb-1" id="reviewDueCount">0</div>
              <div class="text-xs font-bold text-white mb-0.5">Đến Hạn Hôm Nay</div>
              <div class="text-[10px] text-slate-400">Cần củng cố trước nửa đêm</div>
            </div>
            <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 text-center">
              <div class="text-3xl font-black text-amber-400 mb-1" id="reviewTomorrowCount">0</div>
              <div class="text-xs font-bold text-white mb-0.5">Đến Hạn Ngày Mai</div>
              <div class="text-[10px] text-slate-400">Chu kỳ tiếp theo</div>
            </div>
            <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 text-center">
              <div class="text-3xl font-black text-emerald-400 mb-1" id="reviewMasteredCount">0</div>
              <div class="text-xs font-bold text-white mb-0.5">Đã Khắc Sâu (Mastered)</div>
              <div class="text-[10px] text-slate-400">Khoảng cách &gt; 21 ngày</div>
            </div>
          </div>

          <!-- Quick Banner to switch to 3-Way Practice -->
          <div class="p-4 rounded-2xl bg-gradient-to-r from-emerald-950/40 via-teal-950/30 to-slate-900 border border-emerald-500/20 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shrink-0">
                <i class="fa-solid fa-graduation-cap text-lg"></i>
              </div>
              <div>
                <h4 class="text-xs font-bold text-white">Luyện tập sâu với Bài tập Tự luận 3 Chiều</h4>
                <p class="text-[11px] text-slate-400">Tự ghi từ theo phiên âm, kiểm tra phát âm qua microphone và viết từ theo nghĩa tiếng Việt.</p>
              </div>
            </div>
            <button onclick="switchReviewSubTab('exercises')" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold transition shrink-0 flex items-center gap-1.5">
              <span>Luyện tập ngay</span> <i class="fa-solid fa-arrow-right"></i>
            </button>
          </div>

          <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6">
            <h3 class="text-sm font-bold text-white mb-3">Danh sách thẻ cần ôn</h3>
            <div id="reviewDueCardsList" class="space-y-2">
              <!-- Rendered by JS -->
            </div>
          </div>
        </div>

        <!-- SUB-TAB 2: DYNAMIC RANDOMIZED CLOZE QUIZ & 3-WAY PRACTICE -->
        <div id="reviewSubTabExercisesContainer" class="space-y-6">
          <!-- Exercise Mode Selection Toolbar -->
          <div class="bg-slate-900 border border-slate-800 rounded-2xl p-4 flex flex-col lg:flex-row lg:items-center justify-between gap-4">
            <div class="flex flex-wrap items-center gap-2">
              <span class="text-[11px] font-bold text-slate-400 uppercase tracking-wider mr-1">Chế độ giấu đề:</span>
              <button id="btnMultiModeMix" onclick="setMultiExMode('mix')" class="px-3 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 bg-indigo-500/15 text-indigo-300 border border-indigo-500/30 shadow-sm">
                <i class="fa-solid fa-shuffle"></i> <span>🎲 Đảo Đề Ngẫu Nhiên</span>
              </button>
              <button id="btnMultiMode1" onclick="setMultiExMode('mode1')" class="px-3 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 text-slate-400 hover:text-white hover:bg-slate-800 border border-transparent">
                <i class="fa-solid fa-eye-slash"></i> <span>🔤 Kiểu 1: Phiên âm</span>
              </button>
              <button id="btnMultiMode2" onclick="setMultiExMode('mode2')" class="px-3 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 text-slate-400 hover:text-white hover:bg-slate-800 border border-transparent">
                <i class="fa-solid fa-language"></i> <span>📖 Kiểu 2: Từ vựng</span>
              </button>
              <button id="btnMultiMode3" onclick="setMultiExMode('mode3')" class="px-3 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 text-slate-400 hover:text-white hover:bg-slate-800 border border-transparent">
                <i class="fa-solid fa-pen-nib"></i> <span>📝 Kiểu 3: Nghĩa TV</span>
              </button>
              <button id="btnMultiMode4" onclick="setMultiExMode('mode4')" class="px-3 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 text-slate-400 hover:text-white hover:bg-slate-800 border border-transparent">
                <i class="fa-solid fa-puzzle-piece"></i> <span>🧩 Kiểu 4: Giấu Ký Tự (Cloze)</span>
              </button>
            </div>

            <div class="flex items-center gap-2">
              <button onclick="shuffleAndRestartQuiz()" title="Đảo lại thứ tự và cách giấu đề mới cho các từ" class="px-3.5 py-1.5 bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-500 hover:to-amber-400 text-white rounded-xl text-xs font-bold transition flex items-center gap-1.5 shadow-md shadow-amber-600/20">
                <i class="fa-solid fa-arrows-spin"></i> <span>Đảo Lại Đề Thi</span>
              </button>
              <span id="multiExSourceBadge" class="text-[10px] px-2.5 py-1 rounded-md bg-slate-800 border border-slate-700 text-slate-300 font-semibold">
                Nguồn: Đang tải...
              </span>
            </div>
          </div>

          <!-- Interactive Exercise Box -->
          <div id="multiExCardBox" class="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-6 shadow-2xl relative overflow-hidden">
            <!-- Top Progress & Mode Header -->
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800/80 pb-4">
              <div class="flex items-center gap-3">
                <span id="multiExModeBadge" class="px-3 py-1 rounded-xl text-xs font-bold bg-amber-500/15 text-amber-300 border border-amber-500/30 flex items-center gap-1.5">
                  <i class="fa-solid fa-headphones"></i> Kiểu 1: Phiên âm ➔ Viết từ + Nghĩa TV
                </span>
                <span id="multiExLangTag" class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  EN
                </span>
              </div>
              <div class="flex items-center gap-3">
                <span id="multiExProgressText" class="text-xs font-semibold text-slate-400">Câu 1 / 10</span>
                <div class="w-24 sm:w-36 bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div id="multiExProgressBar" class="bg-gradient-to-r from-emerald-500 to-teal-400 h-full transition-all duration-300" style="width: 10%;"></div>
                </div>
              </div>
            </div>

            <!-- Mode Description Guide -->
            <p id="multiExGuideText" class="text-xs text-slate-300 font-medium bg-slate-950/40 p-3 rounded-xl border border-slate-800">
              <!-- Rendered by JS -->
            </p>

            <!-- PROMPT AREA (Adaptive per Mode) -->
            <div class="p-6 sm:p-8 bg-slate-950/70 rounded-2xl border border-slate-800 text-center space-y-3 relative">
              <div class="text-[10px] font-bold text-slate-400 uppercase tracking-widest" id="multiExPromptTitle">ĐỀ BÀI GỢI Ý</div>
              
              <!-- Large Prompt Display -->
              <div id="multiExPromptMain" class="text-3xl sm:text-4xl font-black text-white tracking-wide">
                <!-- Word or IPA or Meaning -->
              </div>

              <!-- Extra Prompt Info: Sub-IPA, POS, or Audio Button -->
              <div id="multiExPromptExtra" class="flex flex-wrap items-center justify-center gap-2 pt-1">
                <!-- Rendered by JS -->
              </div>
            </div>

            <!-- EXERCISE INPUTS SECTION -->
            <div class="space-y-4 max-w-2xl mx-auto">
              <!-- Field 1: Word Writing (Mode 1 & Mode 3) -->
              <div id="multiExWordInputContainer" class="space-y-1.5">
                <label id="multiExWordInputLabel" class="block text-xs font-bold text-slate-200 flex items-center gap-1.5">
                  <i class="fa-solid fa-keyboard text-cyan-400"></i> 1. Tự viết từ tiếng Anh (hoặc chữ Hán):
                </label>
                <div class="relative">
                  <input id="multiExWordInput" type="text" autocomplete="off" placeholder="Gõ từ vựng chính xác..." class="w-full px-4 py-3 rounded-xl bg-slate-800 border border-slate-700 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400 transition font-medium" />
                  <span class="absolute right-3 top-3 text-[10px] text-slate-500 pointer-events-none">Enter</span>
                </div>
              </div>

              <!-- Field 2: Speaking / Pronunciation (Mode 2 & Mode 3) -->
              <div id="multiExSpeakingContainer" class="space-y-2 p-4 rounded-xl bg-slate-950/50 border border-slate-800">
                <label class="block text-xs font-bold text-slate-200 flex items-center gap-1.5">
                  <i class="fa-solid fa-microphone text-teal-400"></i> Phát âm từ vựng chuẩn xác:
                </label>
                <div class="flex flex-wrap items-center gap-3">
                  <button id="btnMultiExMic" onclick="toggleMultiExMic()" class="px-4 py-2.5 bg-teal-600 hover:bg-teal-500 text-white rounded-xl text-xs font-bold transition flex items-center gap-2 shadow-lg shadow-teal-600/20">
                    <i class="fa-solid fa-microphone"></i> <span>Bắt đầu đọc to / Thu âm</span>
                  </button>
                  <button onclick="markMultiExSpoken()" class="px-3.5 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold border border-slate-700 transition flex items-center gap-1.5">
                    <i class="fa-solid fa-check text-emerald-400"></i> <span>Đã tự đọc to</span>
                  </button>
                </div>
                <div id="multiExSpeechStatus" class="text-xs text-slate-400 pt-1">
                  Chưa ghi âm giọng đọc. Bấm nút thu âm và đọc rõ từ vựng.
                </div>
              </div>

              <!-- Field 3: Meaning in Vietnamese (Mode 1 & Mode 2) -->
              <div id="multiExMeaningInputContainer" class="space-y-1.5">
                <label class="block text-xs font-bold text-slate-200 flex items-center gap-1.5">
                  <i class="fa-solid fa-language text-amber-400"></i> Ghi nghĩa tiếng Việt của từ:
                </label>
                <div class="relative">
                  <input id="multiExMeaningInput" type="text" autocomplete="off" placeholder="Nhập nghĩa tiếng Việt..." class="w-full px-4 py-3 rounded-xl bg-slate-800 border border-slate-700 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-amber-400 transition font-medium" />
                  <span class="absolute right-3 top-3 text-[10px] text-slate-500 pointer-events-none">Enter</span>
                </div>
              </div>
            </div>

            <!-- ACTION BUTTONS BAR -->
            <div class="flex flex-wrap items-center justify-between gap-3 pt-2 max-w-2xl mx-auto">
              <div class="flex items-center gap-2">
                <button id="btnMultiExCheck" onclick="checkMultiExAnswer()" class="px-6 py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl text-xs transition flex items-center gap-2 shadow-lg shadow-emerald-600/30">
                  <i class="fa-solid fa-circle-check"></i> Kiểm Tra Đáp Án
                </button>
                <button id="btnMultiExReveal" onclick="revealMultiExAnswer()" class="px-4 py-3 bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold rounded-xl text-xs transition flex items-center gap-1.5">
                  <i class="fa-regular fa-lightbulb text-amber-400"></i> Xem đáp án
                </button>
              </div>

              <button id="btnMultiExNext" onclick="nextMultiExCard()" class="hidden px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl text-xs transition flex items-center gap-2 shadow-lg shadow-indigo-600/30">
                <span>Từ tiếp theo</span> <i class="fa-solid fa-arrow-right"></i>
              </button>
            </div>

            <!-- FEEDBACK AND ANALYSIS CONTAINER (Shown after Checking) -->
            <div id="multiExFeedbackBox" class="hidden space-y-4 max-w-2xl mx-auto pt-4 border-t border-slate-800 animate-fadeIn">
              <!-- Alert Status Header -->
              <div id="multiExStatusAlert" class="p-4 rounded-xl border flex items-center gap-3">
                <!-- Rendered by JS -->
              </div>

              <!-- Side-by-side Answer Comparison Grid -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                <!-- Target Word Details -->
                <div class="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
                  <div class="text-[10px] font-bold text-slate-400 uppercase flex items-center justify-between">
                    <span>Từ vựng chuẩn xác</span>
                    <button id="btnFeedbackAudio" onclick="playMultiExAudio()" class="text-emerald-400 hover:text-emerald-300">
                      <i class="fa-solid fa-volume-high"></i> Nghe lại
                    </button>
                  </div>
                  <div class="text-base font-bold text-white flex items-center gap-2">
                    <span id="feedbackTermText">...</span>
                    <span id="feedbackPosTag" class="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 font-medium">noun</span>
                  </div>
                  <div id="feedbackPhoneticText" class="text-xs text-amber-300 font-mono">/ipa/</div>
                  <div id="feedbackWordUserComparison" class="text-[11px] pt-1">
                    <!-- Comparison with user's written word -->
                  </div>
                </div>

                <!-- Vietnamese Definition Details -->
                <div class="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
                  <div class="text-[10px] font-bold text-slate-400 uppercase">Nghĩa tiếng Việt chuẩn</div>
                  <div id="feedbackMeaningText" class="text-sm font-semibold text-slate-200">
                    ...
                  </div>
                  <div id="feedbackMeaningUserComparison" class="text-[11px] pt-1">
                    <!-- Comparison with user's typed meaning -->
                  </div>
                </div>
              </div>

              <!-- Examples & Root Word Box -->
              <div id="feedbackExtraContextBox" class="hidden p-4 rounded-xl bg-slate-950/50 border border-slate-800 text-xs space-y-2">
                <div id="feedbackRootWordRow" class="hidden text-[11px] text-slate-300">
                  <span class="font-bold text-teal-400"><i class="fa-solid fa-seedling"></i> Từ gốc (Root word):</span> <span id="feedbackRootWordVal"></span>
                </div>
                <div id="feedbackExamplesRow" class="hidden space-y-1">
                  <div class="font-bold text-slate-400 text-[10px] uppercase">Ví dụ minh họa:</div>
                  <ul id="feedbackExamplesList" class="list-disc list-inside text-slate-300 space-y-1"></ul>
                </div>
              </div>
            </div>

            <!-- COMPLETION SUMMARY BOX (Shown when all cards finished) -->
            <div id="multiExCompleteBox" class="hidden text-center py-10 space-y-5">
              <div class="w-16 h-16 rounded-3xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center text-3xl mx-auto shadow-xl">
                <i class="fa-solid fa-trophy"></i>
              </div>
              <div>
                <h3 class="text-xl font-black text-white">Hoàn Thành Xuất Sắc Phiên Luyện Tập!</h3>
                <p id="multiExCompleteStats" class="text-xs text-slate-400 mt-1">Bạn đã hoàn thành toàn bộ bài tập trong lượt này.</p>
              </div>
              <div class="flex flex-wrap items-center justify-center gap-3 pt-2">
                <button onclick="initMultiExSession(true)" class="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold transition flex items-center gap-2">
                  <i class="fa-solid fa-arrows-rotate"></i> Luyện tập thêm lượt mới
                </button>
                <button onclick="switchReviewSubTab('srs')" class="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold border border-slate-700 transition">
                  <i class="fa-solid fa-layer-group"></i> Về danh sách thẻ SRS
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- SUB-TAB 3: SRS RE-LEARNING CENTER (LẶP LẠI NGẮT QUÃNG) -->
        <div id="reviewSubTabRelearnContainer" class="hidden space-y-6">
          <!-- Leitner Box 5-Stage Ladder -->
          <div class="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-6 shadow-xl">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
              <div>
                <h3 class="text-lg font-black text-white flex items-center gap-2">
                  <i class="fa-solid fa-stairs text-teal-400"></i> Bảng Phân Bố Chu Kỳ Lặp Lại Ngắt Quãng (Leitner & SM-2)
                </h3>
                <p class="text-xs text-slate-400 mt-0.5">Các nấc khoảng cách giúp đưa từ vựng từ trí nhớ ngắn hạn vào vỏ não dài hạn vĩnh viễn.</p>
              </div>
              <div class="flex flex-wrap items-center gap-2">
                <button onclick="startLapsedRelearnSession()" class="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-xl text-xs font-bold transition flex items-center gap-2 shadow-lg shadow-rose-600/30">
                  <i class="fa-solid fa-triangle-exclamation"></i> Ôn Ngay Từ Chưa Thuộc (<span id="relearnLapsedBadgeCount">0</span>)
                </button>
                <button onclick="startDailyStructuredSession(true)" class="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-xl text-xs font-semibold transition flex items-center gap-1.5">
                  <i class="fa-solid fa-infinity text-teal-400"></i> Ôn Tự Do Không Giới Hạn
                </button>
              </div>
            </div>

            <!-- 5 Interval Boxes Grid -->
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
              <!-- Box 1 -->
              <div class="bg-slate-950/70 border border-rose-500/30 rounded-2xl p-4 text-center space-y-1 relative overflow-hidden group hover:border-rose-500 transition">
                <div class="text-[10px] font-bold text-rose-400 uppercase tracking-wider flex items-center justify-center gap-1">
                  <span class="w-2 h-2 rounded-full bg-rose-400 inline-block"></span> Nấc 1: 1 Ngày
                </div>
                <div id="relearnBox1" class="text-3xl font-black text-rose-400">0</div>
                <div class="text-[10px] text-slate-400 font-medium">Từ Mới & Chưa Thuộc</div>
                <div class="text-[9px] text-slate-500">Cần lặp lại trong 24h</div>
              </div>

              <!-- Box 2 -->
              <div class="bg-slate-950/70 border border-amber-500/30 rounded-2xl p-4 text-center space-y-1 relative overflow-hidden group hover:border-amber-500 transition">
                <div class="text-[10px] font-bold text-amber-400 uppercase tracking-wider flex items-center justify-center gap-1">
                  <span class="w-2 h-2 rounded-full bg-amber-400 inline-block"></span> Nấc 2: 3 Ngày
                </div>
                <div id="relearnBox2" class="text-3xl font-black text-amber-400">0</div>
                <div class="text-[10px] text-slate-400 font-medium">Trí Nhớ Ngắn Hạn</div>
                <div class="text-[9px] text-slate-500">Đã nhớ lần 1</div>
              </div>

              <!-- Box 3 -->
              <div class="bg-slate-950/70 border border-yellow-500/30 rounded-2xl p-4 text-center space-y-1 relative overflow-hidden group hover:border-yellow-500 transition">
                <div class="text-[10px] font-bold text-yellow-400 uppercase tracking-wider flex items-center justify-center gap-1">
                  <span class="w-2 h-2 rounded-full bg-yellow-400 inline-block"></span> Nấc 3: 7 Ngày
                </div>
                <div id="relearnBox3" class="text-3xl font-black text-yellow-400">0</div>
                <div class="text-[10px] text-slate-400 font-medium">Trí Nhớ Trung Hạn</div>
                <div class="text-[9px] text-slate-500">Củng cố sau 1 tuần</div>
              </div>

              <!-- Box 4 -->
              <div class="bg-slate-950/70 border border-teal-500/30 rounded-2xl p-4 text-center space-y-1 relative overflow-hidden group hover:border-teal-500 transition">
                <div class="text-[10px] font-bold text-teal-400 uppercase tracking-wider flex items-center justify-center gap-1">
                  <span class="w-2 h-2 rounded-full bg-teal-400 inline-block"></span> Nấc 4: 14 Ngày
                </div>
                <div id="relearnBox4" class="text-3xl font-black text-teal-400">0</div>
                <div class="text-[10px] text-slate-400 font-medium">Khắc Sâu Trí Nhớ</div>
                <div class="text-[9px] text-slate-500">Gần đạt phản xạ tự nhiên</div>
              </div>

              <!-- Box 5 -->
              <div class="bg-slate-950/70 border border-emerald-500/30 rounded-2xl p-4 text-center space-y-1 relative overflow-hidden group hover:border-emerald-500 transition">
                <div class="text-[10px] font-bold text-emerald-400 uppercase tracking-wider flex items-center justify-center gap-1">
                  <span class="w-2 h-2 rounded-full bg-emerald-400 inline-block"></span> Nấc 5: 30+ Ngày
                </div>
                <div id="relearnBox5" class="text-3xl font-black text-emerald-400">0</div>
                <div class="text-[10px] text-slate-400 font-medium">Thành Thạo (Mastered)</div>
                <div class="text-[9px] text-slate-500">Trí nhớ dài hạn vĩnh viễn</div>
              </div>
            </div>
          </div>

          <!-- Lapsed / Weak Words Table -->
          <div class="bg-slate-900 border border-slate-800 rounded-3xl p-6 space-y-4">
            <div class="flex items-center justify-between">
              <div>
                <h4 class="text-sm font-bold text-white flex items-center gap-2">
                  <i class="fa-solid fa-triangle-exclamation text-rose-400"></i> Danh Sách Từ Hay Quên & Cần Học Lại (Lapsed Words)
                </h4>
                <p class="text-[11px] text-slate-400 mt-0.5">Những từ từng bị điền sai hoặc note "Chưa thuộc" cần được ôn tập lặp lại ngay.</p>
              </div>
              <button onclick="loadRelearnCenterData()" class="px-2.5 py-1 text-xs text-slate-400 hover:text-white bg-slate-800 rounded-lg border border-slate-700 transition">
                <i class="fa-solid fa-arrows-rotate"></i> Làm mới
              </button>
            </div>

            <div id="relearnLapsedCardsList" class="space-y-2">
              <!-- Rendered by JS -->
            </div>
          </div>
        </div>
      </div>

      <!-- VIEW 7: PRACTICE (Writing & Speaking) -->
      <div id="view-practice" class="hidden space-y-6">
        <div>
          <h1 class="text-2xl font-black text-white">Luyện Tập Ngữ Cảnh & Kỹ Năng</h1>
          <p class="text-xs text-slate-400">Thực hành viết câu và luyện phát âm theo từ vựng đang học</p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Writing Exercise Panel -->
          <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-xl">
            <div class="flex items-center justify-between">
              <h3 class="text-sm font-bold text-white flex items-center gap-2">
                <i class="fa-solid fa-pen-nib text-cyan-400"></i> Luyện Viết Câu (Sentence Writing)
              </h3>
              <span class="text-[10px] px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 font-semibold border border-cyan-500/20">Writing</span>
            </div>

            <div class="bg-slate-950/60 p-4 rounded-xl border border-slate-800">
              <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Đề bài gợi ý:</div>
              <div id="practicePromptText" class="text-xs font-semibold text-slate-200">
                Hãy đặt 1 câu hoàn chỉnh sử dụng từ: <span class="text-emerald-400 font-bold" id="practiceTargetWord">resilient</span> (có nghĩa: có khả năng phục hồi nhanh).
              </div>
            </div>

            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1">Câu trả lời của bạn:</label>
              <textarea id="practiceUserInput" rows="3" class="w-full px-3.5 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-xs text-white focus:outline-none focus:border-brand-500" placeholder="Viết câu của bạn ở đây..."></textarea>
            </div>

            <div class="flex items-center justify-between">
              <button onclick="revealPracticeModelAnswer()" class="text-xs text-slate-400 hover:text-white transition">
                <i class="fa-regular fa-lightbulb"></i> Xem câu mẫu tham khảo
              </button>
              <button onclick="submitPracticeWriting()" class="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white font-bold rounded-xl text-xs transition">
                Gửi Đánh Giá
              </button>
            </div>

            <div id="practiceModelBox" class="hidden bg-slate-950/80 p-3.5 rounded-xl border border-slate-800 text-xs space-y-1">
              <div class="text-[10px] font-bold text-slate-400 uppercase">Câu Mẫu:</div>
              <div id="practiceModelAnswerText" class="text-slate-200 font-medium">The local economy proved remarkably resilient after the crisis.</div>
            </div>
          </div>

          <!-- Pronunciation & Listening Panel -->
          <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-xl">
            <div class="flex items-center justify-between">
              <h3 class="text-sm font-bold text-white flex items-center gap-2">
                <i class="fa-solid fa-microphone text-teal-400"></i> Luyện Phát Âm (Audio & Speech)
              </h3>
              <span class="text-[10px] px-2 py-0.5 rounded bg-teal-500/10 text-teal-400 font-semibold border border-teal-500/20">Audio TTS</span>
            </div>

            <div class="p-6 bg-slate-950/60 rounded-xl border border-slate-800 text-center space-y-4">
              <div id="speakingWordDisplay" class="text-3xl font-black text-white">resilient</div>
              <div id="speakingIpaDisplay" class="text-sm text-slate-400 font-mono">/rɪˈzɪl.jənt/</div>

              <div class="flex items-center justify-center gap-3">
                <button onclick="playPracticeTTS()" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-semibold border border-slate-700 transition flex items-center gap-2">
                  <i class="fa-solid fa-volume-high text-emerald-400"></i> Nghe mẫu chuẩn
                </button>
                <button id="speechRecBtn" onclick="toggleSpeechRecording()" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold transition flex items-center gap-2 shadow-lg shadow-emerald-600/20">
                  <i class="fa-solid fa-microphone"></i> Bắt đầu nói
                </button>
              </div>

              <div id="speechResultBox" class="hidden text-xs p-3 rounded-lg bg-slate-900 border border-slate-800 text-slate-300">
                Nhận diện giọng nói: <span id="speechResultText" class="font-bold text-emerald-300"></span>
              </div>
            </div>
          </div>
        </div>

        <!-- History of Practice Submissions -->
        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6">
          <h3 class="text-sm font-bold text-white mb-4">Lịch Sử Luyện Tập Gần Đây</h3>
          <div id="practiceHistoryTable" class="space-y-2">
            <!-- Rendered by JS -->
          </div>
        </div>
      </div>

      <!-- VIEW 8: IMPORT VOCABULARY WIZARD -->
      <div id="view-importer" class="hidden space-y-6">
        <div>
          <h1 class="text-2xl font-black text-white">Nhập Từ Vựng Vào Hệ Thống</h1>
          <p class="text-xs text-slate-400">Hỗ trợ tệp CSV, Excel (.xlsx), hoặc dán trực tiếp dữ liệu từ Google Sheets/Excel với quan hệ từ gốc (↳ Root word: ...)</p>
        </div>

        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
          <!-- Wizard Tabs: Upload File vs Paste Table -->
          <div class="flex border-b border-slate-800">
            <button id="importTabFile" onclick="switchImportTab('file')" class="pb-3 px-4 text-xs font-bold border-b-2 border-emerald-500 text-emerald-400">
              <i class="fa-solid fa-file-arrow-up mr-1.5"></i> Tải Tệp Lên (.csv / .xlsx)
            </button>
            <button id="importTabPaste" onclick="switchImportTab('paste')" class="pb-3 px-4 text-xs font-bold border-b-2 border-transparent text-slate-400 hover:text-white">
              <i class="fa-solid fa-paste mr-1.5"></i> Dán Bảng Dữ Liệu Trực Tiếp
            </button>
          </div>

          <!-- Configuration row -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1">Nhập vào Bộ Thẻ</label>
              <select id="importTargetDeck" class="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-xs text-slate-200">
                <!-- Populated by JS -->
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1">Chiến Lược Trùng Lặp (Deduplication)</label>
              <select id="importDedupMode" class="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-xl text-xs text-slate-200">
                <option value="skip">Bỏ qua nếu từ đã tồn tại (Skip)</option>
                <option value="merge">Hợp nhất nghĩa và ví dụ (Merge)</option>
                <option value="overwrite">Ghi đè định nghĩa (Overwrite)</option>
                <option value="allow_duplicates">Cho phép trùng lặp (Allow duplicates)</option>
              </select>
            </div>
          </div>

          <!-- TAB CONTENT 1: FILE UPLOAD -->
          <div id="importFileSection" class="space-y-4">
            <div class="border-2 border-dashed border-slate-700 hover:border-emerald-500 rounded-2xl p-8 text-center transition cursor-pointer" onclick="document.getElementById('wizardFileInput').click()">
              <input type="file" id="wizardFileInput" accept=".csv,.xlsx" class="hidden" onchange="handleWizardFileSelected(event)">
              <div class="w-12 h-12 rounded-xl bg-emerald-500/10 text-emerald-400 mx-auto flex items-center justify-center text-xl mb-3">
                <i class="fa-solid fa-cloud-arrow-up"></i>
              </div>
              <div class="text-xs font-bold text-white mb-1">Nhấn để chọn tệp hoặc kéo thả vào đây</div>
              <div class="text-[10px] text-slate-400">Hỗ trợ định dạng .CSV (UTF-8) hoặc Excel .XLSX</div>
              <div id="selectedFileName" class="text-xs font-bold text-emerald-400 mt-2 hidden"></div>
            </div>

            <div class="p-3.5 bg-slate-950/60 rounded-xl border border-slate-800 text-[11px] text-slate-400 space-y-1">
              <div class="font-bold text-slate-300 flex items-center gap-1.5"><i class="fa-solid fa-circle-info text-emerald-400"></i> Hướng dẫn đặt tên cột cho tệp CSV / Excel:</div>
              <p>• <b>Phiên âm:</b> Hỗ trợ tự động nhận diện: <code class="text-emerald-400 font-mono">ipa</code>, <code class="text-emerald-400 font-mono">Phiên âm</code>, <code class="text-emerald-400 font-mono">Phát âm</code>, <code class="text-emerald-400 font-mono">Phiên âm (IPA)</code>, <code class="text-emerald-400 font-mono">Cách đọc</code>, <code class="text-emerald-400 font-mono">Phonetics</code>, <code class="text-emerald-400 font-mono">Pronunciation</code>,...</p>
              <p>• <b>Từ vựng & Định nghĩa:</b> Nhận diện: <code class="text-blue-400 font-mono">term</code>, <code class="text-blue-400 font-mono">word</code>, <code class="text-blue-400 font-mono">từ vựng</code>, <code class="text-purple-400 font-mono">definition</code>, <code class="text-purple-400 font-mono">meaning</code>, <code class="text-purple-400 font-mono">nghĩa</code>, <code class="text-purple-400 font-mono">định nghĩa</code>,...</p>
              <p class="text-slate-500">Bấm <b>"Xem Trước (Preview)"</b> bên dưới để kiểm tra các cột đã nhận diện chuẩn xác trước khi lưu vào hệ thống.</p>
            </div>
          </div>

          <!-- TAB CONTENT 2: PASTE TEXT -->
          <div id="importPasteSection" class="hidden space-y-4">
            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1">Dán dữ liệu bảng phân cách bởi dấu Tab hoặc Phẩy:</label>
              <textarea id="wizardPasteInput" rows="6" class="w-full px-3.5 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-xs text-white font-mono focus:outline-none focus:border-brand-500" placeholder="term&#9;definition&#9;ipa&#9;part_of_speech&#10;resilient&#9;kiên cường phục hồi&#9;/rɪˈzɪl.jənt/&#9;adjective&#10;↳ Root word: resile&#9;quay trở lại trạng thái cũ&#9;&#9;verb"></textarea>
            </div>
          </div>

          <!-- Action buttons -->
          <div class="flex items-center justify-between pt-4 border-t border-slate-800">
            <button onclick="previewImportData()" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-xl text-xs font-semibold transition">
              <i class="fa-solid fa-eye"></i> Xem Trước (Preview)
            </button>
            <button onclick="executeImportData()" class="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl text-xs transition shadow-lg shadow-emerald-600/30">
              <i class="fa-solid fa-check"></i> Xác Nhận Nhập Từ
            </button>
          </div>

          <!-- Preview Table Area -->
          <div id="importPreviewArea" class="hidden space-y-3 pt-4 border-t border-slate-800">
            <div class="flex items-center justify-between">
              <h4 class="text-xs font-bold text-white uppercase tracking-wider">Xem trước kết quả phân tích:</h4>
              <span id="previewCountBadge" class="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold">0 hàng</span>
            </div>
            <!-- Column mapping status badges -->
            <div id="importMappingBadges" class="flex flex-wrap items-center gap-2 text-[11px] p-2.5 rounded-xl bg-slate-950/70 border border-slate-800">
              <!-- Rendered by JS -->
            </div>
            <div class="overflow-x-auto max-h-60 border border-slate-800 rounded-xl scrollbar-thin">
              <table class="w-full text-left text-xs">
                <thead class="bg-slate-800 text-slate-400 text-[10px] uppercase">
                  <tr>
                    <th class="p-2.5">Dòng</th>
                    <th class="p-2.5">Từ vựng (Term)</th>
                    <th class="p-2.5 text-emerald-400">Phiên âm (IPA)</th>
                    <th class="p-2.5">Định nghĩa (Definition)</th>
                    <th class="p-2.5">Loại từ</th>
                    <th class="p-2.5">Quan hệ từ gốc</th>
                  </tr>
                </thead>
                <tbody id="previewTableBody" class="divide-y divide-slate-800 text-slate-300">
                  <!-- Rendered by JS -->
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- VIEW 9: PROGRESS & STREAKS -->
      <div id="view-progress" class="hidden space-y-6">
        <div>
          <h1 class="text-2xl font-black text-white">Tiến Độ & Thói Quen Học Tập</h1>
          <p class="text-xs text-slate-400">Theo dõi chuỗi học tập hàng ngày, biểu đồ hoạt động và phân bổ cấp độ ghi nhớ</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 text-center">
            <div class="text-4xl mb-1">🔥</div>
            <div id="progCurrentStreak" class="text-2xl font-black text-amber-400">0 ngày</div>
            <div class="text-xs font-semibold text-white">Chuỗi hiện tại</div>
          </div>
          <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 text-center">
            <div class="text-4xl mb-1">🏆</div>
            <div id="progLongestStreak" class="text-2xl font-black text-emerald-400">0 ngày</div>
            <div class="text-xs font-semibold text-white">Kỷ lục chuỗi dài nhất</div>
          </div>
          <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 text-center">
            <div class="text-4xl mb-1">📅</div>
            <div id="progActiveDays" class="text-2xl font-black text-cyan-400">0 ngày</div>
            <div class="text-xs font-semibold text-white">Tổng số ngày đã học</div>
          </div>
        </div>

        <!-- 30-Day Activity Heatmap -->
        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
          <h3 class="text-sm font-bold text-white">Mật Độ Hoạt Động 30 Ngày Gần Nhất</h3>
          <div id="activityHeatmap" class="grid grid-cols-6 sm:grid-cols-10 md:grid-cols-15 gap-2">
            <!-- Rendered by JS -->
          </div>
          <div class="flex items-center gap-2 text-[10px] text-slate-400">
            <span>Ít</span>
            <span class="w-3 h-3 rounded bg-slate-800"></span>
            <span class="w-3 h-3 rounded bg-emerald-900"></span>
            <span class="w-3 h-3 rounded bg-emerald-600"></span>
            <span class="w-3 h-3 rounded bg-emerald-400"></span>
            <span>Nhiều</span>
          </div>
        </div>

        <!-- SRS Retention Breakdown -->
        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6">
          <h3 class="text-sm font-bold text-white mb-4">Phân Bổ Cấp Độ Trí Nhớ (SRS Stages)</h3>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
            <div class="bg-slate-950 p-4 rounded-xl border border-slate-800">
              <div class="text-xs text-slate-400 font-medium">Từ Mới (New)</div>
              <div id="srsStageNew" class="text-xl font-bold text-emerald-400 mt-1">0</div>
            </div>
            <div class="bg-slate-950 p-4 rounded-xl border border-slate-800">
              <div class="text-xs text-slate-400 font-medium">Đang Học (Learning)</div>
              <div id="srsStageLearning" class="text-xl font-bold text-amber-400 mt-1">0</div>
            </div>
            <div class="bg-slate-950 p-4 rounded-xl border border-slate-800">
              <div class="text-xs text-slate-400 font-medium">Ôn Tập (Review)</div>
              <div id="srsStageReview" class="text-xl font-bold text-cyan-400 mt-1">0</div>
            </div>
            <div class="bg-slate-950 p-4 rounded-xl border border-slate-800">
              <div class="text-xs text-slate-400 font-medium">Cần Học Lại (Lapsed)</div>
              <div id="srsStageLapsed" class="text-xl font-bold text-rose-400 mt-1">0</div>
            </div>
          </div>
        </div>
      </div>

      <!-- VIEW 10: SETTINGS -->
      <div id="view-settings" class="hidden space-y-6 max-w-2xl">
        <div>
          <h1 class="text-2xl font-black text-white">Cài Đặt Hệ Thống</h1>
          <p class="text-xs text-slate-400">Tùy biến ngôn ngữ học, ngôn ngữ giao diện và mục tiêu hàng ngày</p>
        </div>

        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-5">
          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1">Ngôn Ngữ Giao Diện (Interface Language)</label>
            <select id="settingInterfaceLang" class="w-full px-3.5 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-xs text-white">
              <option value="vi">Tiếng Việt (Mặc định)</option>
              <option value="en">English (Tiếng Anh)</option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1">Ngôn Ngữ Đang Học Hiện Tại (Learning Language)</label>
            <select id="settingLearningLang" onchange="handleSettingLangChange(this.value)" class="w-full px-3.5 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-xs text-white">
              <option value="en">🇬🇧 Tiếng Anh (English)</option>
              <option value="zh">🇨🇳 Tiếng Trung (Mandarin Chinese)</option>
              <option value="ja">🇯🇵 Tiếng Nhật (Japanese)</option>
              <option value="de">🇩🇪 Tiếng Đức (German)</option>
            </select>
          </div>

          <div id="settingScriptPrefGroup" class="hidden">
            <label class="block text-xs font-semibold text-slate-300 mb-1">Bộ Chữ Tiếng Trung (Script Preference)</label>
            <select id="settingScriptPref" class="w-full px-3.5 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-xs text-white">
              <option value="simplified">Chữ Giản Thể (简体字 - Mặc định)</option>
              <option value="traditional">Chữ Phồn Thể (繁體字)</option>
            </select>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1">Giọng Phát Âm Tiếng Anh (TTS)</label>
              <select id="settingEnglishVoice" class="w-full px-3.5 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-xs text-white">
                <option value="en-US">English (Mỹ - en-US)</option>
                <option value="en-GB">English (Anh - en-GB)</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1">Giọng Phát Âm Tiếng Trung (TTS)</label>
              <select id="settingChineseVoice" class="w-full px-3.5 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-xs text-white">
                <option value="zh-CN">Chinese (Phổ thông - zh-CN)</option>
                <option value="zh-TW">Chinese (Đài Loan - zh-TW)</option>
              </select>
            </div>
          </div>

          <div class="grid grid-cols-3 gap-3">
            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1">Từ Mới / Ngày</label>
              <input type="number" id="settingDailyNewTarget" min="1" max="100" value="10" class="w-full px-3.5 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-xs text-white">
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1">Ôn Tập / Ngày</label>
              <input type="number" id="settingDailyReviewTarget" min="5" max="500" value="50" class="w-full px-3.5 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-xs text-white">
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1">Thời Gian (Phút)</label>
              <input type="number" id="settingDailyTimeGoal" min="5" max="120" value="20" class="w-full px-3.5 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-xs text-white">
            </div>
          </div>

          <button onclick="saveUserSettings()" class="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl text-xs transition shadow-lg shadow-emerald-600/30">
            Lưu Thay Đổi Cài Đặt
          </button>
        </div>

        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
          <h3 class="text-sm font-bold text-white flex items-center gap-2">
            <i class="fa-solid fa-database text-cyan-400"></i> Quản Lý Dữ Liệu & Khởi Tạo Mẫu
          </h3>
          <p class="text-xs text-slate-400">Tạo thêm bộ từ vựng mẫu chuẩn hoặc xóa sạch dữ liệu từ vựng để bắt đầu lại với 1 bộ thẻ mẫu duy nhất.</p>
          <div class="flex flex-wrap items-center gap-3 pt-1">
            <button onclick="seedSampleTemplateDeck()" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-semibold rounded-xl text-xs transition flex items-center gap-2">
              <i class="fa-solid fa-wand-magic-sparkles text-amber-400"></i> Tạo Thêm 1 Bộ Thẻ Mẫu
            </button>
            <button onclick="resetAllVocabularyAndSeed()" class="px-4 py-2 bg-rose-600/20 hover:bg-rose-600/30 text-rose-300 border border-rose-500/30 font-bold rounded-xl text-xs transition flex items-center gap-2">
              <i class="fa-solid fa-trash-can text-rose-400"></i> Xóa Hết Từ Vựng & Tạo Lại 1 Bộ Mẫu
            </button>
          </div>
        </div>
      </div>

    </main>
  </div>

  <!-- MODAL: LANGUAGE ONBOARDING (Post-login / Switcher) -->
  <div id="modalLanguageOnboarding" class="hidden fixed inset-0 z-50 bg-slate-950/90 backdrop-blur-md flex items-center justify-center p-4">
    <div class="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 max-w-xl w-full shadow-2xl text-center space-y-6">
      <div class="w-14 h-14 rounded-2xl bg-gradient-to-tr from-brand-600 to-emerald-400 text-white mx-auto flex items-center justify-center text-2xl shadow-lg shadow-brand-500/20">
        <i class="fa-solid fa-earth-asia"></i>
      </div>
      <div>
        <h2 class="text-2xl font-black text-white">Chọn Không Gian Học Tập</h2>
        <p class="text-xs text-slate-400 mt-1 max-w-md mx-auto">Chào mừng bạn đến với VocabMaster! Vui lòng chọn ngôn ngữ chính bạn muốn tập trung học tập. Hệ thống sẽ cá nhân hóa lộ trình, thuật toán SRS và dữ liệu hoàn toàn tách biệt.</p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-left">
        <!-- English Mode Card -->
        <div onclick="selectOnboardingWorkspace('en')" class="p-5 rounded-2xl bg-slate-800/80 hover:bg-slate-800 border-2 border-slate-700 hover:border-emerald-500 cursor-pointer transition group flex flex-col justify-between">
          <div>
            <div class="text-3xl mb-2">🇬🇧</div>
            <h3 class="text-base font-bold text-white group-hover:text-emerald-400 transition">English Mode</h3>
            <p class="text-[11px] text-slate-400 mt-1">Từ vựng tiếng Anh, phiên âm quốc tế IPA, các loại từ, ví dụ ngữ cảnh, họ từ vựng và audio US/UK.</p>
          </div>
          <button class="mt-4 w-full py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold transition">
            Vào Không Gian Tiếng Anh
          </button>
        </div>

        <!-- Chinese Mode Card -->
        <div onclick="selectOnboardingWorkspace('zh')" class="p-5 rounded-2xl bg-slate-800/80 hover:bg-slate-800 border-2 border-slate-700 hover:border-amber-500 cursor-pointer transition group flex flex-col justify-between">
          <div>
            <div class="text-3xl mb-2">🇨🇳</div>
            <h3 class="text-base font-bold text-white group-hover:text-amber-400 transition">Chinese Mode</h3>
            <p class="text-[11px] text-slate-400 mt-1">Hán tự Giản thể & Phồn thể, phiên âm Pinyin thanh điệu chuẩn, phân cấp chứng chỉ HSK 1-6 và audio zh-CN.</p>
          </div>
          <button class="mt-4 w-full py-2 bg-amber-600 hover:bg-amber-500 text-white rounded-xl text-xs font-bold transition">
            Vào Không Gian Tiếng Trung
          </button>
        </div>
      </div>
      <p class="text-[11px] text-slate-500">Bạn luôn có thể chuyển đổi linh hoạt giữa 2 không gian bất kỳ lúc nào trên thanh điều hướng trên cùng.</p>
    </div>
  </div>

  <!-- MODAL: CREATE DECK / COLLECTION -->
  <div id="modalCreateDeck" class="hidden fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-md w-full shadow-2xl my-8">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h3 class="text-sm font-bold text-white">Tạo Bộ Thẻ / Danh Mục Mới</h3>
          <p class="text-xs text-slate-400 mt-0.5">Thiết lập mục tiêu và giới hạn học tập hàng ngày</p>
        </div>
        <button onclick="closeModal('modalCreateDeck')" class="text-slate-400 hover:text-white"><i class="fa-solid fa-xmark"></i></button>
      </div>
      <form onsubmit="handleCreateDeck(event)" class="space-y-3.5">
        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">Tên Bộ Thẻ *</label>
          <input type="text" id="deckModalName" required class="w-full px-3.5 py-2 rounded-xl bg-slate-800 border border-slate-700 text-xs text-white" placeholder="e.g. Từ Vựng Giao Tiếp Chuyên Ngành">
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">Ngôn Ngữ</label>
          <select id="deckModalLang" class="w-full px-3.5 py-2 rounded-xl bg-slate-800 border border-slate-700 text-xs text-white">
            <option value="en">English (🇬🇧 Tiếng Anh)</option>
            <option value="zh">Chinese (🇨🇳 Tiếng Trung)</option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">Thẻ Phân Loại (Tags - cách nhau bằng dấu phẩy)</label>
          <input type="text" id="deckModalTags" class="w-full px-3.5 py-2 rounded-xl bg-slate-800 border border-slate-700 text-xs text-white" placeholder="e.g. ielts, giao tiep, business">
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1">Từ mới tối đa/ngày</label>
            <input type="number" id="deckModalMaxNew" value="10" min="1" max="100" class="w-full px-3.5 py-2 rounded-xl bg-slate-800 border border-slate-700 text-xs text-white">
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1">Ôn tập tối đa/ngày</label>
            <input type="number" id="deckModalMaxRev" value="50" min="5" max="300" class="w-full px-3.5 py-2 rounded-xl bg-slate-800 border border-slate-700 text-xs text-white">
          </div>
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">Mô Tả (Tùy chọn)</label>
          <textarea id="deckModalDesc" rows="2" class="w-full px-3.5 py-2 rounded-xl bg-slate-800 border border-slate-700 text-xs text-white" placeholder="e.g. Nhóm từ vựng phục vụ công việc và phỏng vấn"></textarea>
        </div>
        <div class="flex items-center justify-end gap-3 pt-2">
          <button type="button" onclick="closeModal('modalCreateDeck')" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold transition">
            Hủy Bỏ
          </button>
          <button type="submit" class="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl text-xs transition">
            Tạo Bộ Thẻ
          </button>
        </div>
      </form>
    </div>
  </div>

  <!-- MODAL: EDIT / RENAME DECK -->
  <div id="modalEditDeck" class="hidden fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-md w-full shadow-2xl my-8">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h3 class="text-sm font-bold text-white flex items-center gap-2">
            <i class="fa-solid fa-pen-to-square text-emerald-400"></i> Đổi Tên & Chỉnh Sửa Bộ Thẻ
          </h3>
          <p class="text-xs text-slate-400 mt-0.5">Cập nhật tên gọi và mô tả của bộ từ vựng</p>
        </div>
        <button onclick="closeModal('modalEditDeck')" class="text-slate-400 hover:text-white"><i class="fa-solid fa-xmark"></i></button>
      </div>
      <form onsubmit="handleEditDeck(event)" class="space-y-3.5">
        <input type="hidden" id="editDeckTargetId" value="">
        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">Tên Bộ Thẻ Mới <span class="text-rose-400">*</span></label>
          <input type="text" id="editDeckNameInput" required class="w-full px-3.5 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-xs text-white focus:outline-none focus:border-emerald-500 font-medium" placeholder="Nhập tên mới cho bộ từ vựng...">
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">Mô Tả (Tùy chọn)</label>
          <textarea id="editDeckDescInput" rows="2" class="w-full px-3.5 py-2 rounded-xl bg-slate-800 border border-slate-700 text-xs text-white focus:outline-none focus:border-emerald-500" placeholder="Mô tả bộ từ vựng..."></textarea>
        </div>
        <div class="flex items-center justify-end gap-3 pt-2">
          <button type="button" onclick="closeModal('modalEditDeck')" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold transition">
            Hủy Bỏ
          </button>
          <button type="submit" class="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl text-xs transition flex items-center gap-1.5 shadow-lg shadow-emerald-600/30">
            <i class="fa-solid fa-floppy-disk"></i> Lưu Thay Đổi
          </button>
        </div>
      </form>
    </div>
  </div>

  <!-- MODAL: SAFE DELETE DECK CONFIRMATION -->
  <div id="modalDeleteDeck" class="hidden fixed inset-0 z-50 bg-slate-950/85 backdrop-blur-sm flex items-center justify-center p-4">
    <div class="bg-slate-900 border border-slate-800 rounded-3xl p-6 max-w-md w-full shadow-2xl space-y-4">
      <div class="flex items-center gap-3 text-rose-400">
        <i class="fa-solid fa-triangle-exclamation text-2xl"></i>
        <h3 class="text-base font-bold text-white">Xác Nhận Xóa Bộ Thẻ</h3>
      </div>
      <p class="text-xs text-slate-300" id="deleteDeckPromptText">Bạn có chắc chắn muốn xóa bộ thẻ này? Hãy chọn phương thức xử lý từ vựng bên trong:</p>
      <input type="hidden" id="deleteDeckTargetId" value="">
      <div class="space-y-2">
        <button onclick="executeDeckDeletion(false)" class="w-full p-3 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-left transition flex items-center justify-between">
          <div>
            <div class="text-xs font-bold text-emerald-400"><i class="fa-solid fa-shield-halved mr-1"></i> Xóa An Toàn (Khuyên dùng)</div>
            <div class="text-[10px] text-slate-400 mt-0.5">Giữ lại toàn bộ từ vựng & thẻ SRS, chuyển vào danh mục "Từ Vựng Chung".</div>
          </div>
          <i class="fa-solid fa-arrow-right text-slate-500 text-xs"></i>
        </button>
        <button onclick="executeDeckDeletion(true)" class="w-full p-3 rounded-xl bg-rose-950/30 hover:bg-rose-950/60 border border-rose-800/40 text-left transition flex items-center justify-between">
          <div>
            <div class="text-xs font-bold text-rose-400"><i class="fa-solid fa-trash-can mr-1"></i> Xóa Vĩnh Viễn</div>
            <div class="text-[10px] text-rose-300/60 mt-0.5">Xóa vĩnh viễn cả bộ thẻ và toàn bộ từ vựng bên trong. Không thể khôi phục.</div>
          </div>
          <i class="fa-solid fa-arrow-right text-rose-500 text-xs"></i>
        </button>
      </div>
      <button onclick="closeModal('modalDeleteDeck')" class="w-full py-2 bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white rounded-xl text-xs font-semibold transition">
        Đóng / Hủy Bỏ
      </button>
    </div>
  </div>

  <!-- MODAL: CREATE VOCABULARY ITEM MANUALLY -->
  <div id="modalCreateVocab" class="hidden fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-lg w-full shadow-2xl my-8">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h3 class="text-sm font-bold text-white flex items-center gap-2">
            <i class="fa-solid fa-plus-circle text-emerald-400"></i> Thêm Từ Vựng Mới Thủ Công
          </h3>
          <p class="text-xs text-slate-400 mt-0.5">Thêm từ, phiên âm IPA, giải nghĩa tiếng Việt và câu ví dụ</p>
        </div>
        <button onclick="closeModal('modalCreateVocab')" class="text-slate-400 hover:text-white"><i class="fa-solid fa-xmark"></i></button>
      </div>
      <form onsubmit="handleCreateVocabManual(event)" class="space-y-3.5">
        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">Chọn Bộ Thẻ *</label>
          <select id="manualVocabDeck" required class="w-full px-3.5 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-xs text-white focus:outline-none focus:border-brand-500">
            <!-- Populated by JS -->
          </select>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label id="manualVocabTermLabel" class="block text-xs font-semibold text-slate-300 mb-1">Từ Vựng (Word) *</label>
            <input type="text" id="manualVocabTerm" required class="w-full px-3.5 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-xs text-white font-bold focus:outline-none focus:border-brand-500" placeholder="e.g. serendipity">
          </div>
          <div>
            <label id="manualVocabIpaLabel" class="block text-xs font-semibold text-slate-300 mb-1">Phiên Âm (IPA)</label>
            <div class="relative">
              <input type="text" id="manualVocabIpa" class="w-full pl-3.5 pr-8 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-xs text-white font-mono focus:outline-none focus:border-brand-500" placeholder="e.g. /ˌser.ənˈdɪp.ə.ti/">
              <button type="button" onclick="previewManualTts()" title="Nghe thử phát âm (TTS)" class="absolute right-2.5 top-2.5 text-slate-400 hover:text-emerald-400 text-xs">
                <i class="fa-solid fa-volume-high"></i>
              </button>
            </div>
          </div>
        </div>

        <div id="vocabEnglishFields" class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1">Loại Từ (Part of Speech)</label>
            <select id="manualVocabPos" class="w-full px-3.5 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-xs text-white focus:outline-none focus:border-brand-500">
              <option value="noun">Danh từ (noun)</option>
              <option value="verb">Động từ (verb)</option>
              <option value="adjective">Tính từ (adjective)</option>
              <option value="adverb">Trạng từ (adverb)</option>
              <option value="phrase">Cụm từ / Thành ngữ (phrase)</option>
              <option value="preposition">Giới từ (preposition)</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1">Từ Gốc / Họ Từ Liên Quan (Tùy chọn)</label>
            <input type="text" id="manualVocabRoot" class="w-full px-3.5 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-xs text-white focus:outline-none focus:border-brand-500" placeholder="e.g. serene, chance">
          </div>
        </div>

        <div id="vocabChineseFields" class="hidden grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1">Cấp Độ HSK</label>
            <select id="manualVocabHsk" class="w-full px-3.5 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-xs text-white focus:outline-none focus:border-brand-500">
              <option value="HSK 1">HSK 1 (Cơ bản)</option>
              <option value="HSK 2">HSK 2</option>
              <option value="HSK 3">HSK 3 (Trung cấp)</option>
              <option value="HSK 4">HSK 4</option>
              <option value="HSK 5">HSK 5 (Cao cấp)</option>
              <option value="HSK 6">HSK 6 (Thành thạo)</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1">Chữ Phồn Thể / Bộ Thủ (Tùy chọn)</label>
            <input type="text" id="manualVocabTrad" class="w-full px-3.5 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-xs text-white focus:outline-none focus:border-brand-500" placeholder="e.g. 繁體字 / 部首">
          </div>
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">Định Nghĩa / Nghĩa Tiếng Việt *</label>
          <input type="text" id="manualVocabDef" required class="w-full px-3.5 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-xs text-white focus:outline-none focus:border-brand-500" placeholder="e.g. sự may mắn tình cờ, cơ duyên bất ngờ">
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">Câu Ví Dụ Minh Họa (Tùy chọn)</label>
          <textarea id="manualVocabExample" rows="2" class="w-full px-3.5 py-2 rounded-xl bg-slate-800 border border-slate-700 text-xs text-white focus:outline-none focus:border-brand-500" placeholder="e.g. Meeting each other was pure serendipity."></textarea>
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">Mẹo Ghi Nhớ (Mnemonic - Tùy chọn)</label>
          <input type="text" id="manualVocabMnemonic" class="w-full px-3.5 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-xs text-white focus:outline-none focus:border-brand-500" placeholder="e.g. 'serene' (thanh thản) + 'dip' (nhúng vào may mắn)">
        </div>

        <div class="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
          <button type="button" onclick="closeModal('modalCreateVocab')" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold transition">
            Hủy Bỏ
          </button>
          <button type="submit" class="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl text-xs transition shadow-lg shadow-emerald-600/30 flex items-center gap-1.5">
            <i class="fa-solid fa-check"></i> Lưu Từ Vựng
          </button>
        </div>
      </form>
    </div>
  </div>

  <!-- MODAL: CREATE LEARNING PATH -->
  <div id="modalCreatePath" class="hidden fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-md w-full shadow-2xl">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-sm font-bold text-white">Tạo Lộ Trình Học Tập Mới</h3>
        <button onclick="closeModal('modalCreatePath')" class="text-slate-400 hover:text-white"><i class="fa-solid fa-xmark"></i></button>
      </div>
      <form onsubmit="handleCreatePath(event)" class="space-y-4">
        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">Tên Lộ Trình</label>
          <input type="text" id="pathModalName" required class="w-full px-3.5 py-2 rounded-xl bg-slate-800 border border-slate-700 text-xs text-white" placeholder="e.g. English — TOEIC 800+">
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">Ngôn Ngữ</label>
          <select id="pathModalLang" class="w-full px-3.5 py-2 rounded-xl bg-slate-800 border border-slate-700 text-xs text-white">
            <option value="en">English (en)</option>
            <option value="zh">Chinese (zh)</option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">Mục Tiêu Đạt Được</label>
          <input type="text" id="pathModalObjective" class="w-full px-3.5 py-2 rounded-xl bg-slate-800 border border-slate-700 text-xs text-white" placeholder="e.g. Đạt 850 điểm trong 3 tháng">
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1">Từ mới / ngày</label>
            <input type="number" id="pathModalDailyNew" value="10" min="1" max="50" class="w-full px-3.5 py-2 rounded-xl bg-slate-800 border border-slate-700 text-xs text-white">
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1">Thời gian (phút)</label>
            <input type="number" id="pathModalDailyTime" value="25" min="5" max="120" class="w-full px-3.5 py-2 rounded-xl bg-slate-800 border border-slate-700 text-xs text-white">
          </div>
        </div>
        <button type="submit" class="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl text-xs transition">
          Lưu Lộ Trình
        </button>
      </form>
    </div>
  </div>

  <!-- MODAL: SESSION COMPLETED SUMMARY -->
  <div id="modalSessionSummary" class="hidden fixed inset-0 z-50 bg-slate-950/85 backdrop-blur-sm flex items-center justify-center p-4">
    <div class="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 max-w-md w-full shadow-2xl text-center space-y-6">
      <div class="w-16 h-16 rounded-2xl bg-emerald-500/20 text-emerald-400 mx-auto flex items-center justify-center text-3xl shadow-inner">
        <i class="fa-solid fa-trophy"></i>
      </div>
      <div>
        <h3 class="text-2xl font-black text-white mb-1">Chúc Mừng! Phiên Học Hoàn Tất</h3>
        <p class="text-xs text-slate-400">Bạn đã hoàn thành các giai đoạn của phiên học theo thuật toán lặp lại ngắt quãng.</p>
      </div>

      <div class="grid grid-cols-2 gap-3 bg-slate-950/60 p-4 rounded-2xl border border-slate-800">
        <div>
          <div class="text-[11px] text-slate-400 mb-1">Thẻ Đã Học</div>
          <div id="summaryCardsCount" class="text-2xl font-bold text-white">0</div>
        </div>
        <div>
          <div class="text-[11px] text-slate-400 mb-1">Độ Chính Xác</div>
          <div id="summaryAccuracy" class="text-2xl font-bold text-emerald-400">0%</div>
        </div>
      </div>

      <button onclick="closeModal('modalSessionSummary'); navigateTo('dashboard')" class="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl text-xs transition shadow-lg shadow-emerald-600/30">
        Quay Về Trang Chủ
      </button>
    </div>
  </div>

  <!-- MODAL: VOCABULARY STUDY HISTORY & RETENTION -->
  <div id="modalVocabHistory" class="hidden fixed inset-0 z-50 bg-slate-950/85 backdrop-blur-sm flex items-center justify-center p-4">
    <div class="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 max-w-2xl w-full shadow-2xl space-y-5 max-h-[90vh] flex flex-col animate-fadeIn">
      <div class="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <div class="flex items-center gap-2">
            <h3 class="text-xl font-black text-white" id="histModalTerm">...</h3>
            <span id="histModalPos" class="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-teal-300 border border-slate-700">noun</span>
            <span id="histModalPhonetic" class="text-xs text-amber-300 font-mono">/ipa/</span>
          </div>
          <div id="histModalDefinition" class="text-xs text-slate-300 mt-1">Định nghĩa tiếng Việt</div>
        </div>
        <button onclick="closeModal('modalVocabHistory')" class="text-slate-400 hover:text-white p-2">
          <i class="fa-solid fa-xmark text-lg"></i>
        </button>
      </div>

      <!-- Quick Metrics Grid -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div class="bg-slate-950/70 p-3 rounded-xl border border-slate-800 text-center">
          <div class="text-[10px] text-slate-400 font-medium">Tổng Lượt Học</div>
          <div id="histModalTotalAttempts" class="text-xl font-black text-white mt-0.5">0</div>
        </div>
        <div class="bg-slate-950/70 p-3 rounded-xl border border-slate-800 text-center">
          <div class="text-[10px] text-slate-400 font-medium">Lần Thuộc (Đúng)</div>
          <div id="histModalCorrectCount" class="text-xl font-black text-emerald-400 mt-0.5">0</div>
        </div>
        <div class="bg-slate-950/70 p-3 rounded-xl border border-slate-800 text-center">
          <div class="text-[10px] text-slate-400 font-medium">Chưa Thuộc (Quên)</div>
          <div id="histModalIncorrectCount" class="text-xl font-black text-rose-400 mt-0.5">0</div>
        </div>
        <div class="bg-slate-950/70 p-3 rounded-xl border border-slate-800 text-center">
          <div class="text-[10px] text-slate-400 font-medium">Chu Kỳ Kế Tiếp</div>
          <div id="histModalNextInterval" class="text-xl font-black text-cyan-400 mt-0.5">1 ngày</div>
        </div>
      </div>

      <!-- Retention Progress Bar -->
      <div class="bg-slate-950/50 p-3 rounded-xl border border-slate-800/80 space-y-1.5">
        <div class="flex items-center justify-between text-xs">
          <span class="text-slate-400 text-[11px] font-semibold">Tỷ lệ nhớ / thuộc từ vựng:</span>
          <span id="histModalRetentionRate" class="font-bold text-teal-300">0%</span>
        </div>
        <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
          <div id="histModalRetentionBar" class="bg-gradient-to-r from-emerald-500 to-teal-400 h-full transition-all duration-300" style="width: 0%;"></div>
        </div>
      </div>

      <!-- Timeline History Table -->
      <div class="flex-1 overflow-y-auto space-y-2 pr-1 min-h-[160px]">
        <div class="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Dòng thời gian các lần ôn tập:</div>
        <div id="histModalTimelineList" class="space-y-2">
          <!-- Rendered by JS -->
        </div>
      </div>

      <div class="pt-2 border-t border-slate-800 flex justify-end">
        <button onclick="closeModal('modalVocabHistory')" class="px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-semibold transition border border-slate-700">
          Đóng
        </button>
      </div>
    </div>
  </div>

  <!-- JAVASCRIPT APPLICATION CORE -->
  <script>
    // State management
    let authToken = localStorage.getItem('vocabmaster_token') || null;
    let currentUser = null;
    let currentLearningLanguage = 'en';
    let currentView = 'dashboard';
    let currentSession = null;
    let currentCard = null;
    let allDecks = [];
    let allVocabItems = [];
    let isFlipped = false;
    let selectedWizardFile = null;
    let favoriteFilterOnly = false;

    // API Helper with authentication headers
    async function apiRequest(endpoint, options = {}) {
      const headers = options.headers || {};
      if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
      }
      if (!options.isFormData && !headers['Content-Type']) {
        headers['Content-Type'] = 'application/json';
      }

      const res = await fetch(endpoint, {
        ...options,
        headers
      });

      if (!res.ok) {
        if (res.status === 401) {
          logout();
          throw new Error('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.');
        }
        let detail = 'Có lỗi xảy ra';
        try {
          const errData = await res.json();
          detail = errData.detail || errData.message || detail;
        } catch (_) {}
        throw new Error(detail);
      }

      return await res.json();
    }

    // Speech TTS Helper
    function speakText(text, lang = 'en') {
      if (!('speechSynthesis' in window)) return;
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      if (lang === 'zh') utterance.lang = 'zh-CN';
      else if (lang === 'ja') utterance.lang = 'ja-JP';
      else if (lang === 'de') utterance.lang = 'de-DE';
      else if (lang === 'vi') utterance.lang = 'vi-VN';
      else utterance.lang = 'en-US';
      utterance.rate = 0.9;
      window.speechSynthesis.speak(utterance);
    }

    function speakCurrentWord() {
      if (!currentCard) return;
      speakText(currentCard.term, currentCard.language || currentLearningLanguage);
    }

    // Responsive Mobile Sidebar Drawer Controls
    function toggleMobileSidebar() {
      const sidebar = document.getElementById('appSidebar');
      if (!sidebar) return;
      if (sidebar.classList.contains('-translate-x-full')) {
        openMobileSidebar();
      } else {
        closeMobileSidebar();
      }
    }

    function openMobileSidebar() {
      const sidebar = document.getElementById('appSidebar');
      const backdrop = document.getElementById('sidebarBackdrop');
      if (sidebar) {
        sidebar.classList.remove('-translate-x-full');
      }
      if (backdrop) {
        backdrop.classList.remove('hidden');
      }
      document.body.classList.add('overflow-hidden', 'md:overflow-auto');
    }

    function closeMobileSidebar() {
      const sidebar = document.getElementById('appSidebar');
      const backdrop = document.getElementById('sidebarBackdrop');
      if (sidebar) {
        sidebar.classList.add('-translate-x-full');
      }
      if (backdrop) {
        backdrop.classList.add('hidden');
      }
      document.body.classList.remove('overflow-hidden', 'md:overflow-auto');
    }

    window.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        closeMobileSidebar();
      }
    });

    // Navigation Switcher
    function navigateTo(viewName) {
      closeMobileSidebar();
      if (!authToken && viewName !== 'auth') {
        return navigateTo('auth');
      }

      currentView = viewName;
      // Hide all views
      const views = [
        'auth', 'dashboard', 'paths', 'vocab', 'flashcards',
        'daily-session', 'reviews', 'practice', 'importer', 'progress', 'settings'
      ];
      views.forEach(v => {
        const el = document.getElementById(`view-${v}`);
        if (el) el.classList.add('hidden');
        const navEl = document.getElementById(`nav-${v}`);
        if (navEl) {
          navEl.classList.remove('text-emerald-400', 'bg-emerald-500/10', 'font-semibold');
          navEl.classList.add('text-slate-400', 'font-medium');
        }
      });

      // Show selected view
      const target = document.getElementById(`view-${viewName}`);
      if (target) target.classList.remove('hidden');

      const targetNav = document.getElementById(`nav-${viewName}`);
      if (targetNav) {
        targetNav.classList.remove('text-slate-400', 'font-medium');
        targetNav.classList.add('text-emerald-400', 'bg-emerald-500/10', 'font-semibold');
      }

      // Load specific view data
      if (viewName === 'dashboard') loadDashboard();
      else if (viewName === 'paths') loadPathsView();
      else if (viewName === 'vocab') loadVocabView();
      else if (viewName === 'flashcards') loadFlashcardsView();
      else if (viewName === 'reviews') loadReviewCenterView();
      else if (viewName === 'practice') loadPracticeView();
      else if (viewName === 'importer') loadImporterView();
      else if (viewName === 'progress') loadProgressView();
      else if (viewName === 'settings') loadSettingsView();
    }

    // Auth tab switcher
    function switchAuthTab(tab) {
      const isLogin = tab === 'login';
      document.getElementById('tabLogin').className = isLogin 
        ? 'flex-1 pb-3 text-xs font-bold border-b-2 border-emerald-500 text-emerald-400' 
        : 'flex-1 pb-3 text-xs font-bold border-b-2 border-transparent text-slate-400 hover:text-slate-200';
      document.getElementById('tabRegister').className = !isLogin 
        ? 'flex-1 pb-3 text-xs font-bold border-b-2 border-emerald-500 text-emerald-400' 
        : 'flex-1 pb-3 text-xs font-bold border-b-2 border-transparent text-slate-400 hover:text-slate-200';

      document.getElementById('usernameGroup').classList.toggle('hidden', isLogin);
      document.getElementById('authSubmitBtn').textContent = isLogin ? 'Đăng Nhập' : 'Tạo Tài Khoản Mới';
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
        navigateTo('dashboard');
      } catch (err) {
        errBox.textContent = err.message;
        errBox.classList.remove('hidden');
      }
    }

    async function quickDemoLogin() {
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
        navigateTo('dashboard');
      } catch (_) {
        const reg = await apiRequest('/api/auth/register', {
          method: 'POST',
          body: JSON.stringify({ username: 'learner', email: demoEmail, password: demoPassword })
        });
        authToken = reg.access_token;
        localStorage.setItem('vocabmaster_token', authToken);
        await fetchUserProfile();

        // Seed initial deck & words
        const deck = await apiRequest('/api/decks', {
          method: 'POST',
          body: JSON.stringify({ name: 'Tiếng Anh Công Nghệ (Tech Vocab)', target_language: 'en', description: 'Từ vựng cốt lõi' })
        });
        const sampleCSV = "term,definition,ipa,part_of_speech\\niteration,sự lặp lại một chu trình,/ˌɪt.əˈreɪ.ʃən/,noun\\nconcurrency,tính năng xử lý đồng thời,/kənˈkʌr.ən.si/,noun\\nresilience,khả năng phục hồi vượt khó,/rɪˈzɪl.jəns/,noun\\n↳ Root word: resile,phục hồi về trạng thái ban đầu,,verb";
        const blob = new Blob([sampleCSV], { type: 'text/csv' });
        const formData = new FormData();
        formData.append('file', blob, 'starter.csv');
        await apiRequest(`/api/decks/${deck.id}/import`, {
          method: 'POST',
          body: formData,
          isFormData: true
        });

        navigateTo('dashboard');
      }
    }

    function logout() {
      authToken = null;
      currentUser = null;
      localStorage.removeItem('vocabmaster_token');
      updateAuthHeaderUI();
      navigateTo('auth');
    }

    function updateAuthHeaderUI() {
      const ctrl = document.getElementById('authControls');
      const headerContext = document.getElementById('headerStudyContext');
      if (authToken && currentUser) {
        ctrl.innerHTML = `
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center text-xs font-bold uppercase">
              ${currentUser.username ? currentUser.username[0] : 'U'}
            </div>
            <button onclick="logout()" title="Đăng xuất" class="px-2.5 py-1 text-xs text-rose-400 hover:text-rose-300 bg-slate-800 hover:bg-slate-700 rounded-lg border border-slate-700 transition">
              <i class="fa-solid fa-right-from-bracket"></i>
            </button>
          </div>
        `;
        if (headerContext) headerContext.classList.remove('hidden');
      } else {
        ctrl.innerHTML = `
          <button onclick="navigateTo('auth')" class="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold transition">
            Đăng Nhập
          </button>
        `;
        if (headerContext) headerContext.classList.add('hidden');
      }
    }

    function updateWorkspaceBadge() {
      const badge = document.getElementById('headerWorkspaceBadge');
      if (!badge) return;
      if (currentLearningLanguage === 'zh') {
        badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span><span class="font-bold text-amber-300">🇨🇳 Chinese Mode</span>`;
        badge.className = "flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-xs text-amber-300 shadow-sm";
      } else {
        badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span><span class="font-bold text-emerald-300">🇬🇧 English Mode</span>`;
        badge.className = "flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-300 shadow-sm";
      }
    }

    async function fetchUserProfile() {
      try {
        currentUser = await apiRequest('/api/auth/me');
        currentLearningLanguage = currentUser.active_learning_language || currentUser.learning_language || 'en';
        const hSelect = document.getElementById('headerLangSelect');
        if (hSelect) hSelect.value = currentLearningLanguage;
        const mSelect = document.getElementById('mobileLangSelect');
        if (mSelect) mSelect.value = currentLearningLanguage;
        updateWorkspaceBadge();
        updateAuthHeaderUI();
        if (!currentUser.has_selected_language) {
          openModal('modalLanguageOnboarding');
        }
      } catch (e) {
        logout();
      }
    }

    async function selectOnboardingWorkspace(lang) {
      currentLearningLanguage = lang;
      try {
        await apiRequest('/api/users/workspace', {
          method: 'POST',
          body: JSON.stringify({ language: lang })
        });
        if (currentUser) {
          currentUser.has_selected_language = true;
          currentUser.active_learning_language = lang;
        }
        closeModal('modalLanguageOnboarding');
        const hSelect = document.getElementById('headerLangSelect');
        if (hSelect) hSelect.value = lang;
        const mSelect = document.getElementById('mobileLangSelect');
        if (mSelect) mSelect.value = lang;
        updateWorkspaceBadge();
        navigateTo('dashboard');
      } catch (err) {
        alert(err.message);
      }
    }

    async function switchLearningLanguage(newLang) {
      currentLearningLanguage = newLang;
      const hSelect = document.getElementById('headerLangSelect');
      if (hSelect) hSelect.value = newLang;
      const mSelect = document.getElementById('mobileLangSelect');
      if (mSelect) mSelect.value = newLang;
      updateWorkspaceBadge();
      if (authToken) {
        try {
          await apiRequest('/api/users/workspace', {
            method: 'POST',
            body: JSON.stringify({ language: newLang })
          });
          if (currentUser) currentUser.active_learning_language = newLang;
        } catch (e) {
          console.error("Workspace save error:", e);
        }
      }
      navigateTo(currentView);
    }

    function openDeleteDeckModal(deckId, deckName) {
      document.getElementById('deleteDeckTargetId').value = deckId;
      document.getElementById('deleteDeckPromptText').textContent = 
        `Bạn có chắc chắn muốn xóa bộ thẻ "${deckName}"? Hãy chọn phương thức xử lý các từ vựng bên trong:`;
      openModal('modalDeleteDeck');
    }

    async function executeDeckDeletion(deleteVocab) {
      const deckId = document.getElementById('deleteDeckTargetId').value;
      if (!deckId) return;
      try {
        await apiRequest(`/api/decks/${deckId}?delete_vocabulary=${deleteVocab}`, {
          method: 'DELETE'
        });
        closeModal('modalDeleteDeck');
        if (currentView === 'dashboard') loadDashboard();
        else navigateTo('dashboard');
      } catch (err) {
        alert('Lỗi: ' + err.message);
      }
    }

    function openEditDeckModal(deckId, deckName, deckDesc) {
      document.getElementById('editDeckTargetId').value = deckId;
      document.getElementById('editDeckNameInput').value = deckName || '';
      document.getElementById('editDeckDescInput').value = deckDesc || '';
      openModal('modalEditDeck');
      setTimeout(() => document.getElementById('editDeckNameInput')?.focus(), 50);
    }

    async function handleEditDeck(e) {
      e.preventDefault();
      const deckId = document.getElementById('editDeckTargetId').value;
      const newName = document.getElementById('editDeckNameInput').value.trim();
      const newDesc = document.getElementById('editDeckDescInput').value.trim();

      if (!newName) {
        alert('Vui lòng nhập tên bộ từ vựng!');
        return;
      }

      try {
        await apiRequest(`/api/decks/${deckId}`, {
          method: 'PUT',
          body: JSON.stringify({
            name: newName,
            description: newDesc
          })
        });

        closeModal('modalEditDeck');
        alert('Đã đổi tên bộ thẻ thành công!');
        if (currentView === 'dashboard') loadDashboard();
        else if (currentView === 'flashcards') loadFlashcardsView();
        else navigateTo('dashboard');
      } catch (err) {
        alert('Lỗi khi cập nhật bộ thẻ: ' + err.message);
      }
    }

    function editCurrentFlashcardDeck() {
      const sel = document.getElementById('flashcardDeckSelector');
      const deckId = sel?.value;
      if (!deckId) return alert('Chưa chọn bộ thẻ nào!');
      const deck = (allDecks || []).find(d => d.id === deckId);
      openEditDeckModal(deckId, deck ? deck.name : '', deck ? deck.description : '');
    }

    async function seedSampleTemplateDeck() {
      try {
        const res = await apiRequest(`/api/decks/seed-template?language=${currentLearningLanguage}`, {
          method: 'POST'
        });
        alert(`Đã tạo bộ từ vựng mẫu "${res.name}" với 5 từ vựng tiêu chuẩn! Bạn có thể bấm nút "Đổi tên" để chỉnh sửa tên bộ thẻ theo ý muốn.`);
        loadDashboard();
      } catch (err) {
        alert('Lỗi tạo bộ thẻ mẫu: ' + err.message);
      }
    }

    async function resetAllVocabularyAndSeed() {
      if (!confirm('Bạn có chắc chắn muốn xóa TOÀN BỘ từ vựng hiện tại và tạo 1 bộ thẻ mẫu chuẩn duy nhất không? Hành động này sẽ làm sạch kho từ vựng.')) {
        return;
      }
      try {
        await apiRequest(`/api/decks/reset-all?language=${currentLearningLanguage}`, {
          method: 'POST'
        });
        alert('Đã xóa toàn bộ từ vựng và tạo lại 1 bộ thẻ mẫu chuẩn thành công! Bạn có thể đổi tên bộ thẻ ngay.');
        loadDashboard();
      } catch (err) {
        alert('Lỗi: ' + err.message);
      }
    }

    // Modal Helpers
    function openModal(id) { document.getElementById(id).classList.remove('hidden'); }
    function closeModal(id) { document.getElementById(id).classList.add('hidden'); }

    // DASHBOARD LOADING
    async function loadDashboard() {
      try {
        const [decks, activeRes, streakRes] = await Promise.all([
          apiRequest(`/api/decks?language=${currentLearningLanguage}`),
          apiRequest(`/api/sessions/active?learning_language=${currentLearningLanguage}`),
          apiRequest(`/api/progress/streak?language=${currentLearningLanguage}`)
        ]);

        allDecks = decks;
        document.getElementById('dashTotalDecks').textContent = decks.length;
        document.getElementById('dashStreak').textContent = `${streakRes.current_streak} ngày`;
        document.getElementById('dashLongestStreak').textContent = streakRes.longest_streak;
        document.getElementById('sidebarStreakCount').textContent = streakRes.current_streak;

        let totalWords = 0;
        let dueCards = 0;
        let newCards = 0;

        decks.forEach(d => {
          const t = d.stats?.total_cards ?? d.total_cards ?? 0;
          const due = d.stats?.due_cards ?? d.due_reviews ?? 0;
          const n = d.stats?.new_cards ?? d.new_cards ?? 0;
          totalWords += t;
          dueCards += due;
          newCards += n;
        });

        document.getElementById('dashTotalWords').textContent = totalWords;
        document.getElementById('dashDueCards').textContent = dueCards;
        document.getElementById('dashNewCards').textContent = newCards;

        // Active Session Banner
        const banner = document.getElementById('activeSessionBanner');
        if (activeRes.active && activeRes.session) {
          currentSession = activeRes.session;
          banner.classList.remove('hidden');
          document.getElementById('activeSessionDesc').textContent = 
            `Phiên học: "${activeRes.session.title}" đang tạm dừng tại thẻ ${activeRes.session.current_index + 1}/${activeRes.session.total_cards}.`;
        } else {
          banner.classList.add('hidden');
        }

        // Render Decks Grid
        const grid = document.getElementById('dashDecksGrid');
        grid.innerHTML = '';
        if (decks.length === 0) {
          grid.innerHTML = `
            <div class="col-span-3 text-center py-12 bg-slate-900 border border-slate-800 rounded-2xl p-6">
              <i class="fa-solid fa-folder-open text-4xl text-slate-500 mb-3"></i>
              <div class="text-base font-bold text-slate-200">Chưa có bộ từ vựng nào trong không gian ${currentLearningLanguage === 'zh' ? 'Tiếng Trung' : 'Tiếng Anh'}</div>
              <p class="text-xs text-slate-400 mt-1 mb-5 max-w-md mx-auto">
                Bảng tổng quan đang trống. Bạn có thể tạo ngay 1 bộ thẻ mẫu tiêu chuẩn có sẵn từ vựng để bắt đầu học và đổi tên theo ý muốn!
              </p>
              <div class="flex flex-wrap items-center justify-center gap-3">
                <button onclick="seedSampleTemplateDeck()" class="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold transition flex items-center gap-2 shadow-lg shadow-emerald-600/30">
                  <i class="fa-solid fa-wand-magic-sparkles"></i> Tạo Bộ Từ Vựng Mẫu Chuẩn
                </button>
                <button onclick="openCreateDeckModal()" class="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-xl text-xs font-semibold transition">
                  Tạo Bộ Thẻ Trống
                </button>
              </div>
            </div>
          `;
          return;
        }

        decks.forEach(d => {
          const card = document.createElement('div');
          card.className = "bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-2xl p-5 shadow-lg flex flex-col justify-between transition group";
          const dTotal = d.stats?.total_cards ?? d.total_cards ?? 0;
          const dDue = d.stats?.due_cards ?? d.due_reviews ?? 0;
          const dNew = d.stats?.new_cards ?? d.new_cards ?? 0;
          const tagsHtml = (d.tags && d.tags.length > 0)
            ? `<div class="flex flex-wrap gap-1 mt-2">${d.tags.map(t => `<span class="px-1.5 py-0.5 rounded text-[9px] bg-slate-800 text-slate-300 font-medium">#${t}</span>`).join('')}</div>`
            : '';
          card.innerHTML = `
            <div>
              <div class="flex items-center justify-between mb-2">
                <span class="px-2.5 py-0.5 rounded text-[10px] font-bold ${d.target_language === 'zh' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'} uppercase">${d.target_language === 'zh' ? '🇨🇳 ZH' : '🇬🇧 EN'}</span>
                <div class="flex items-center gap-2">
                  <span class="text-xs text-slate-400 font-semibold">${dTotal} từ</span>
                  <button onclick="openEditDeckModal('${d.id}', '${d.name.replace(/'/g, "\\'")}', '${(d.description || '').replace(/'/g, "\\'")}')" title="Đổi tên bộ thẻ" class="px-2 py-1 text-slate-400 hover:text-emerald-300 hover:bg-slate-800 rounded-lg transition flex items-center gap-1 text-[11px] font-medium border border-slate-700/60">
                    <i class="fa-solid fa-pen-to-square text-xs text-emerald-400"></i> Đổi tên
                  </button>
                  <button onclick="openDeleteDeckModal('${d.id}', '${d.name.replace(/'/g, "\\'")}')" title="Xóa bộ thẻ" class="p-1 text-slate-500 hover:text-rose-400 rounded transition"><i class="fa-solid fa-trash-can text-xs"></i></button>
                </div>
              </div>
              <h4 class="text-base font-bold text-white group-hover:text-emerald-300 transition truncate">${d.name}</h4>
              <p class="text-xs text-slate-400 mt-1 line-clamp-2">${d.description || 'Không có mô tả'}</p>
              ${tagsHtml}
            </div>
            <div class="mt-4 pt-4 border-t border-slate-800 flex items-center justify-between">
              <div class="flex items-center gap-2 text-xs">
                <span class="text-rose-400 font-bold">${dDue} đến hạn</span>
                <span class="text-slate-600">•</span>
                <span class="text-emerald-400 font-bold">${dNew} mới</span>
              </div>
              <div class="flex items-center gap-1.5">
                <button onclick="openEditDeckModal('${d.id}', '${d.name.replace(/'/g, "\\'")}', '${(d.description || '').replace(/'/g, "\\'")}')" class="px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-lg transition border border-slate-700">
                  <i class="fa-solid fa-pen text-[10px]"></i> Sửa
                </button>
                <button onclick="startDeckSession('${d.id}')" class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-lg transition shadow">
                  Học Bộ Này
                </button>
              </div>
            </div>
          `;
          grid.appendChild(card);
        });
      } catch (err) {
        console.error("Dashboard error:", err);
      }
    }

    // LEARNING PATHS VIEW
    async function loadPathsView() {
      try {
        const paths = await apiRequest(`/api/paths?language=${currentLearningLanguage}`);
        const container = document.getElementById('pathsList');
        container.innerHTML = '';
        if (paths.length === 0) {
          container.innerHTML = `
            <div class="col-span-2 text-center py-12 bg-slate-900 border border-slate-800 rounded-2xl">
              <i class="fa-solid fa-route text-3xl text-slate-500 mb-2"></i>
              <div class="text-sm font-bold text-slate-300">Chưa có lộ trình học nào</div>
              <p class="text-xs text-slate-500 mt-1 mb-4">Tạo lộ trình để xâu chuỗi nhiều bộ từ vựng theo mục tiêu cụ thể</p>
              <button onclick="openCreatePathModal()" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold transition">
                Tạo Lộ Trình Đầu Tiên
              </button>
            </div>
          `;
          return;
        }

        paths.forEach(p => {
          const item = document.createElement('div');
          item.className = "bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg space-y-4";
          item.innerHTML = `
            <div class="flex items-center justify-between">
              <div>
                <span class="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold uppercase">${p.learning_language}</span>
                <h3 class="text-base font-bold text-white mt-1">${p.name}</h3>
              </div>
              <span class="text-xs font-semibold px-2 py-1 bg-slate-800 text-slate-300 rounded-lg">${p.total_vocabulary_count} từ</span>
            </div>
            <p class="text-xs text-slate-400">${p.description || p.objective || 'Chưa có mô tả mục tiêu'}</p>
            <div class="text-xs text-slate-400 flex items-center justify-between border-t border-slate-800 pt-3">
              <div>Mục tiêu: <strong class="text-white">${p.daily_new_target} từ/ngày</strong></div>
              <div>Bộ thẻ liên kết: <strong class="text-white">${p.linked_deck_ids ? p.linked_deck_ids.length : 0}</strong></div>
            </div>
            <button onclick="startPathSession('${p.id}')" class="w-full py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold transition">
              Bắt Đầu Học Lộ Trình Này
            </button>
          `;
          container.appendChild(item);
        });
      } catch (err) {
        console.error("Paths error:", err);
      }
    }

    // VOCABULARY LIBRARY VIEW
    let debounceTimer = null;
    function debounceFilterVocab() {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => filterVocabTable(), 250);
    }

    function toggleFavoriteFilter() {
      favoriteFilterOnly = !favoriteFilterOnly;
      const btn = document.getElementById('vocabFilterFavBtn');
      if (favoriteFilterOnly) {
        btn.classList.add('bg-amber-500/10', 'text-amber-400', 'border-amber-500/30');
      } else {
        btn.classList.remove('bg-amber-500/10', 'text-amber-400', 'border-amber-500/30');
      }
      filterVocabTable();
    }

    async function loadVocabView() {
      try {
        const [decks, items] = await Promise.all([
          apiRequest(`/api/decks?language=${currentLearningLanguage}`),
          apiRequest(`/api/vocab?language=${currentLearningLanguage}&limit=200`)
        ]);

        allVocabItems = items;
        const sel = document.getElementById('vocabFilterDeck');
        sel.innerHTML = '<option value="">Tất cả bộ thẻ</option>';
        decks.forEach(d => {
          sel.innerHTML += `<option value="${d.id}">${d.name}</option>`;
        });

        renderVocabRows(items);
      } catch (err) {
        console.error("Vocab load error:", err);
      }
    }

    function filterVocabTable() {
      const q = document.getElementById('vocabSearchInput').value.toLowerCase().trim();
      const deckId = document.getElementById('vocabFilterDeck').value;
      const pos = document.getElementById('vocabFilterPos').value;

      const filtered = allVocabItems.filter(item => {
        if (deckId && item.deck_id !== deckId) return false;
        if (pos && item.part_of_speech.toLowerCase() !== pos.toLowerCase()) return false;
        if (favoriteFilterOnly && !item.is_favorite) return false;
        if (q) {
          const matchTerm = item.term.toLowerCase().includes(q);
          const matchDef = (item.definition || '').toLowerCase().includes(q);
          const matchIpa = (item.ipa || '').toLowerCase().includes(q);
          const matchRoot = (item.root_word || '').toLowerCase().includes(q);
          return matchTerm || matchDef || matchIpa || matchRoot;
        }
        return true;
      });

      renderVocabRows(filtered);
    }

    function renderVocabRows(items) {
      const tbody = document.getElementById('vocabTableBody');
      const empty = document.getElementById('vocabEmptyNotice');
      tbody.innerHTML = '';

      if (items.length === 0) {
        empty.classList.remove('hidden');
        return;
      }
      empty.classList.add('hidden');

      items.forEach(it => {
        const tr = document.createElement('tr');
        tr.className = "hover:bg-slate-800/40 transition";
        const rootBadge = it.root_word ? `<span class="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 text-[10px] font-medium flex items-center gap-1 w-max"><i class="fa-solid fa-code-branch"></i> ${it.root_word}</span>` : '<span class="text-slate-600">—</span>';
        const favIcon = it.is_favorite ? 'fa-solid fa-star text-amber-400' : 'fa-regular fa-star text-slate-600 hover:text-amber-400';

        tr.innerHTML = `
          <td class="px-4 py-3 font-bold text-white flex items-center gap-2">
            <button onclick="toggleFav('${it.id}')" class="transition"><i class="${favIcon}"></i></button>
            <span class="${it.language === 'zh' ? 'font-cjk text-sm' : ''}">${it.term}</span>
            <button onclick="speakText('${it.term}', '${it.language}')" class="text-slate-500 hover:text-emerald-400 text-[11px]"><i class="fa-solid fa-volume-high"></i></button>
          </td>
          <td class="px-4 py-3 text-slate-400 font-mono text-[11px]">${it.language_specific_fields?.pinyin || it.ipa || '—'}</td>
          <td class="px-4 py-3"><span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-800 text-teal-300 border border-slate-700">${it.part_of_speech || '—'}</span></td>
          <td class="px-4 py-3 text-slate-300 font-medium max-w-xs truncate">${it.definition}</td>
          <td class="px-4 py-3">${rootBadge}</td>
          <td class="px-4 py-3 text-center">
            <span class="px-2 py-0.5 rounded text-[9px] font-bold bg-slate-800 text-slate-300 border border-slate-700 uppercase">SRS Ready</span>
          </td>
          <td class="px-4 py-3 text-right whitespace-nowrap">
            <button onclick="openVocabHistoryModal('${it.id}')" title="Xem lịch sử học và chu kỳ SRS" class="text-slate-400 hover:text-cyan-300 p-1.5 transition rounded-lg hover:bg-slate-800"><i class="fa-solid fa-clock-rotate-left"></i></button>
            <button onclick="deleteVocabItem('${it.id}')" title="Xóa từ vựng" class="text-slate-500 hover:text-rose-400 p-1.5 transition rounded-lg hover:bg-slate-800"><i class="fa-solid fa-trash-can"></i></button>
          </td>
        `;
        tbody.appendChild(tr);
      });
    }

    async function toggleFav(vocabId) {
      try {
        const res = await apiRequest(`/api/vocab/${vocabId}/favorite`, { method: 'POST' });
        const item = allVocabItems.find(v => v.id === vocabId);
        if (item) item.is_favorite = res.is_favorite;
        filterVocabTable();
      } catch (e) {
        console.error(e);
      }
    }

    async function deleteVocabItem(vocabId) {
      if (!confirm('Bạn có chắc chắn muốn xóa từ vựng này không?')) return;
      try {
        await apiRequest(`/api/vocab/${vocabId}`, { method: 'DELETE' });
        allVocabItems = allVocabItems.filter(v => v.id !== vocabId);
        filterVocabTable();
      } catch (e) {
        alert(e.message);
      }
    }

    // FLASHCARDS VIEW
    async function loadFlashcardsView() {
      const decks = await apiRequest(`/api/decks?language=${currentLearningLanguage}`);
      const sel = document.getElementById('flashcardDeckSelector');
      sel.innerHTML = '';
      decks.forEach(d => {
        sel.innerHTML += `<option value="${d.id}">${d.name}</option>`;
      });
      if (decks.length > 0) loadDeckFlashcards(decks[0].id);
    }

    async function loadDeckFlashcards(deckId) {
      const items = await apiRequest(`/api/vocab?deck_id=${deckId}&limit=50`);
      const container = document.getElementById('flashcardBrowseDeckContainer');
      container.innerHTML = '';
      items.forEach(it => {
        const div = document.createElement('div');
        div.className = "bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-2xl p-5 shadow-lg space-y-3 cursor-pointer group";
        div.onclick = () => speakText(it.term, it.language);
        div.innerHTML = `
          <div class="flex items-center justify-between text-xs text-slate-400">
            <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-teal-300 border border-slate-700">${it.part_of_speech || 'word'}</span>
            <span class="font-mono">${it.ipa || ''}</span>
          </div>
          <div class="text-2xl font-black text-white group-hover:text-emerald-300 transition">${it.term}</div>
          <div class="text-xs text-slate-300 border-t border-slate-800 pt-2">${it.definition}</div>
        `;
        container.appendChild(div);
      });
    }

    // STUDY SESSION ENGINE (Daily 20-min & Quick Reviews)
    async function startDailyStructuredSession(unlimited = false) {
      closeMobileSidebar();
      try {
        const res = await apiRequest('/api/sessions/start', {
          method: 'POST',
          body: JSON.stringify({
            session_type: 'daily_20min',
            learning_language: currentLearningLanguage,
            unlimited: unlimited
          })
        });
        currentSession = res.session;
        currentCard = res.current_card;
        if (!currentCard || res.session.total_cards === 0) {
          if (res.session.status === 'EMPTY') {
            alert('Kho từ vựng của bạn đang trống! Hãy thêm từ mới hoặc tải lên tệp CSV/Excel trong phần "Nhập Dữ Liệu" để bắt đầu học.');
            return;
          }
          if (!unlimited) {
            if (confirm('Bạn đã hoàn thành toàn bộ mục tiêu thẻ học hôm nay theo giới hạn hàng ngày! Bạn có muốn học tiếp ở chế độ Ôn Tập Không Giới Hạn (Unlimited Mode) để củng cố thêm từ vựng không?')) {
              startDailyStructuredSession(true);
            }
          } else {
            alert('Hiện tại tất cả từ vựng đều đang ở chu kỳ nhớ tốt. Bạn có thể làm quiz trắc nghiệm đảo đề tại Trung Tâm Ôn Tập.');
          }
          return;
        }
        openActiveSessionUI();
      } catch (err) {
        alert(err.message);
      }
    }

    async function startDeckSession(deckId) {
      try {
        const res = await apiRequest('/api/sessions/start', {
          method: 'POST',
          body: JSON.stringify({ deck_id: deckId, session_type: 'deck_study' })
        });
        currentSession = res.session;
        currentCard = res.current_card;
        openActiveSessionUI();
      } catch (err) {
        alert(err.message);
      }
    }

    async function startPathSession(pathId) {
      try {
        const res = await apiRequest('/api/sessions/start', {
          method: 'POST',
          body: JSON.stringify({ path_id: pathId, session_type: 'daily_20min' })
        });
        currentSession = res.session;
        currentCard = res.current_card;
        openActiveSessionUI();
      } catch (err) {
        alert(err.message);
      }
    }

    async function startQuickReviewSession() {
      try {
        const res = await apiRequest('/api/sessions/start', {
          method: 'POST',
          body: JSON.stringify({ session_type: 'review_only', learning_language: currentLearningLanguage })
        });
        currentSession = res.session;
        currentCard = res.current_card;
        openActiveSessionUI();
      } catch (err) {
        alert(err.message);
      }
    }

    async function resumeActiveSession() {
      try {
        const res = await apiRequest(`/api/sessions/${currentSession.id}/resume`, { method: 'POST' });
        currentSession = res.session;
        const activeInfo = await apiRequest(`/api/sessions/active?learning_language=${currentLearningLanguage}`);
        currentCard = activeInfo.current_card;
        openActiveSessionUI();
      } catch (err) {
        alert(err.message);
      }
    }

    function openActiveSessionUI() {
      navigateTo('daily-session');
      isFlipped = false;
      renderCurrentSessionCard();
    }

    function renderCurrentSessionCard() {
      if (!currentCard || !currentSession) {
        // Session ended
        openModal('modalSessionSummary');
        return;
      }

      isFlipped = false;
      document.getElementById('cardAnswerSection').classList.add('hidden');
      document.getElementById('cardRevealContainer').classList.remove('hidden');

      // Update Phase Badge
      const phaseNames = {
        'review': 'Giai đoạn 1: Ôn tập nhanh (Due Cards)',
        'new_words': 'Giai đoạn 2: Từ vựng mới (New Words)',
        'recall_test': 'Giai đoạn 3: Kiểm tra Active Recall',
        'practice': 'Giai đoạn 4: Luyện tập ngữ cảnh',
        'deck_study': 'Ôn tập bộ thẻ',
      };
      document.getElementById('sessionPhaseBadge').textContent = phaseNames[currentSession.current_phase] || 'Phiên học';
      document.getElementById('sessionDeckTitle').textContent = currentSession.title;

      const curIdx = (currentSession.current_index || 0) + 1;
      const total = currentSession.total_cards || 1;
      document.getElementById('sessionCardIndexText').textContent = `Thẻ ${curIdx} / ${total}`;
      const pct = Math.min(100, Math.round((curIdx / total) * 100));
      document.getElementById('sessionProgressBar').style.width = `${pct}%`;

      // Word details with strict language isolation
      const isChinese = (currentCard.language === 'zh' || currentLearningLanguage === 'zh');
      document.getElementById('cardLangTag').textContent = isChinese ? 'ZH' : 'EN';
      document.getElementById('cardLangTag').className = isChinese
        ? 'px-2.5 py-1 rounded-md text-[10px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20 uppercase'
        : 'px-2.5 py-1 rounded-md text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 uppercase';
      document.getElementById('cardSrsState').textContent = currentCard.state || 'REVIEW';
      document.getElementById('cardMainTerm').textContent = currentCard.term;

      const attrContainer = document.getElementById('cardLangAttributes');
      if (isChinese) {
        // Chinese Mode: Pinyin with tones, never substitute IPA
        const pinyin = currentCard.language_specific_fields?.pinyin || '';
        document.getElementById('cardMainIpa').textContent = pinyin ? `${pinyin}` : '';
        document.getElementById('cardMainIpa').className = 'text-sm text-amber-300 font-sans tracking-wide font-medium';
        const hsk = currentCard.language_specific_fields?.hsk_level;
        if (hsk) {
          attrContainer.innerHTML = `<span class="px-2 py-0.5 rounded bg-amber-500/15 text-amber-300 border border-amber-500/30 text-xs font-bold">HSK ${hsk}</span>`;
        } else {
          attrContainer.innerHTML = '';
        }
        document.getElementById('cardMainPos').textContent = currentCard.part_of_speech || 'Hán tự';
      } else {
        // English Mode: IPA pronunciation, never Pinyin
        document.getElementById('cardMainIpa').textContent = currentCard.ipa ? `${currentCard.ipa}` : '';
        document.getElementById('cardMainIpa').className = 'text-sm text-slate-400 font-mono tracking-wider';
        attrContainer.innerHTML = '';
        document.getElementById('cardMainPos').textContent = currentCard.part_of_speech || 'từ vựng';
      }
      document.getElementById('cardMainMeaning').textContent = currentCard.definition;

      // Root word link
      const rootBox = document.getElementById('cardRootWordBox');
      if (currentCard.root_word) {
        rootBox.classList.remove('hidden');
        document.getElementById('cardRootWordText').textContent = currentCard.root_word;
      } else {
        rootBox.classList.add('hidden');
      }

      // Examples
      const exBox = document.getElementById('cardExamplesBox');
      const exList = document.getElementById('cardExamplesList');
      exList.innerHTML = '';
      if (currentCard.examples && currentCard.examples.length > 0) {
        exBox.classList.remove('hidden');
        currentCard.examples.forEach(ex => {
          const li = document.createElement('li');
          li.textContent = ex;
          exList.appendChild(li);
        });
      } else {
        exBox.classList.add('hidden');
      }
    }

    function revealStudyAnswer() {
      isFlipped = true;
      document.getElementById('cardAnswerSection').classList.remove('hidden');
      document.getElementById('cardRevealContainer').classList.add('hidden');
    }

    async function submitStudyAnswer(rating) {
      if (!currentSession) return;
      try {
        const res = await apiRequest(`/api/sessions/${currentSession.id}/answer`, {
          method: 'POST',
          body: JSON.stringify({ rating: rating, time_spent_seconds: 3.0 })
        });

        currentSession = res.session;
        if (res.is_completed) {
          const summary = await apiRequest(`/api/sessions/${currentSession.id}/summary`);
          document.getElementById('summaryCardsCount').textContent = summary.completed_cards;
          document.getElementById('summaryAccuracy').textContent = `${summary.accuracy_percentage}%`;
          openModal('modalSessionSummary');
        } else {
          currentCard = res.next_card;
          renderCurrentSessionCard();
        }
      } catch (err) {
        alert(err.message);
      }
    }

    async function pauseStudySession() {
      if (!currentSession) return;
      await apiRequest(`/api/sessions/${currentSession.id}/pause`, { method: 'POST' });
      navigateTo('dashboard');
    }

    async function abandonStudySession() {
      if (!confirm('Bạn có muốn tạm dừng và thoát khỏi phiên học này?')) return;
      if (currentSession) {
        await apiRequest(`/api/sessions/${currentSession.id}/pause`, { method: 'POST' });
      }
      navigateTo('dashboard');
    }

    // Keyboard Shortcuts (Space to flip, 0-5 to rate)
    document.addEventListener('keydown', (e) => {
      if (currentView !== 'daily-session') return;
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

      if (e.code === 'Space') {
        e.preventDefault();
        if (!isFlipped) revealStudyAnswer();
      } else if (isFlipped && e.key >= '0' && e.key <= '5') {
        e.preventDefault();
        submitStudyAnswer(parseInt(e.key, 10));
      }
    });

    // REVIEW CENTER VIEW & 3-WAY MULTIMODAL PRACTICE ENGINE
    let reviewActiveSubTab = 'exercises';
    let multiExMode = 'mix'; // 'mix' | 'mode1' | 'mode2' | 'mode3'
    let multiExCards = [];
    let multiExIndex = 0;
    let multiExScore = { correct: 0, partial: 0, wrong: 0, total: 0 };
    let multiExRecognition = null;
    let multiExSpeechTranscript = '';
    let multiExSpokenVerified = false;
    let isMultiExListening = false;
    let currentActiveExerciseMode = 'mode1';
    let isMultiExChecked = false;
    let isMultiExRevealed = false;

    function switchReviewSubTab(subTab) {
      reviewActiveSubTab = subTab;

      const btnExercises = document.getElementById('btnSubTabReviewExercises');
      const btnSRS = document.getElementById('btnSubTabReviewSRS');
      const btnRelearn = document.getElementById('btnSubTabReviewRelearn');
      const containerExercises = document.getElementById('reviewSubTabExercisesContainer');
      const containerSRS = document.getElementById('reviewSubTabSRSContainer');
      const containerRelearn = document.getElementById('reviewSubTabRelearnContainer');

      const activeClass = 'px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-2 bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shadow-sm';
      const inactiveClass = 'px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-2 text-slate-400 hover:text-white hover:bg-slate-800/60 border border-transparent';

      if (btnExercises) btnExercises.className = (subTab === 'exercises') ? activeClass : inactiveClass;
      if (btnSRS) btnSRS.className = (subTab === 'srs') ? activeClass : inactiveClass;
      if (btnRelearn) btnRelearn.className = (subTab === 'relearn') ? activeClass : inactiveClass;

      if (containerExercises) containerExercises.classList.toggle('hidden', subTab !== 'exercises');
      if (containerSRS) containerSRS.classList.toggle('hidden', subTab !== 'srs');
      if (containerRelearn) containerRelearn.classList.toggle('hidden', subTab !== 'relearn');

      if (subTab === 'exercises' && (!multiExCards || multiExCards.length === 0)) {
        initMultiExSession();
      } else if (subTab === 'relearn') {
        loadRelearnCenterData();
      }
    }

    function setMultiExMode(mode) {
      multiExMode = mode;
      const modes = ['mix', 'mode1', 'mode2', 'mode3', 'mode4'];
      modes.forEach(m => {
        let btnId = 'btnMultiModeMix';
        if (m === 'mode1') btnId = 'btnMultiMode1';
        else if (m === 'mode2') btnId = 'btnMultiMode2';
        else if (m === 'mode3') btnId = 'btnMultiMode3';
        else if (m === 'mode4') btnId = 'btnMultiMode4';
        const btn = document.getElementById(btnId);
        if (btn) {
          if (m === mode) {
            btn.className = 'px-3 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 bg-indigo-500/15 text-indigo-300 border border-indigo-500/30 shadow-sm';
          } else {
            btn.className = 'px-3 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 text-slate-400 hover:text-white hover:bg-slate-800 border border-transparent';
          }
        }
      });
      renderMultiExCard();
    }

    function makeCloze(word) {
      if (!word) return '';
      return word.split('').map((ch, idx) => {
        if (ch === ' ' || ch === '-' || ch === "'") return ch;
        return (idx % 2 === 1) ? '＿' : ch;
      }).join(' ');
    }

    function evaluateVietnameseMeaningSimilarity(userText, targetText, threshold = 0.52) {
      if (!userText || !targetText) return { is_similar: false, score: 0, percentage: 0, feedback: 'Chưa nhập nghĩa tiếng Việt' };
      
      const clean = (s) => (s || '').toLowerCase().replace(/[.,/#!$%^&*;:{}=\-_`~()?\"'\[\]\\<>+]/g, ' ').replace(/\s+/g, ' ').trim();
      const userNorm = clean(userText);
      const targetNorm = clean(targetText);

      const particles = ['sự', 'tính', 'việc', 'cuộc', 'cái', 'con', 'người', 'nhà', 'nơi', 'chỗ', 'đồ', 'vật', 'được', 'bị', 'làm', 'khiến', 'tình trạng'];
      const stripPart = (str) => {
        let words = str.split(' ');
        while (words.length > 0 && particles.includes(words[0])) {
          words.shift();
        }
        return words.join(' ');
      };

      const userCore = stripPart(userNorm);

      const senses = targetText.split(/[;,/|\n()]/).map(clean).filter(s => s.length > 1);
      if (senses.length === 0) senses.push(targetNorm);

      const synGroups = [
        ['kiên trì', 'bền chí', 'kiên nhẫn', 'bền bỉ', 'nhẫn nại', 'chịu khó', 'kiên cường'],
        ['phổ biến', 'thông thường', 'khắp nơi', 'rộng rãi', 'đại trà', 'quen thuộc', 'ở khắp mọi nơi', 'có mặt khắp nơi'],
        ['quan trọng', 'thiết yếu', 'cốt yếu', 'chủ chốt', 'then chốt', 'trọng yếu'],
        ['thành công', 'đạt được', 'thắng lợi', 'thành tựu', 'thành đạt'],
        ['thất bại', 'hỏng', 'bại', 'đổ vỡ', 'thua cuộc'],
        ['thông minh', 'sáng dạ', 'nhanh trí', 'lanh lợi', 'khôn ngoan', 'tài giỏi'],
        ['khó khăn', 'gian nan', 'vất vả', 'trở ngại', 'thử thách'],
        ['nhanh', 'mau', 'chóng', 'lẹ', 'tốc độ', 'nhanh chóng', 'mau chóng'],
        ['chậm', 'từ từ', 'chậm chạp', 'chậm trễ', 'trì trệ'],
        ['to lớn', 'khổng lồ', 'vĩ đại', 'rộng lớn', 'bao la'],
        ['nhỏ bé', 'bé nhỏ', 'tí hon', 'ít ỏi'],
        ['đẹp', 'xinh', 'xinh xắn', 'xinh đẹp', 'dễ nhìn', 'ưa nhìn'],
        ['xấu', 'tệ', 'xấu xí', 'dở', 'kém', 'tồi tệ'],
        ['bắt đầu', 'khởi đầu', 'mở đầu', 'tiến hành'],
        ['kết thúc', 'hoàn thành', 'chấm dứt', 'xong'],
        ['tìm kiếm', 'tìm', 'lùng', 'tra cứu'],
        ['giúp đỡ', 'hỗ trợ', 'cứu trợ', 'giúp'],
        ['bảo vệ', 'gìn giữ', 'phòng hộ', 'che chở'],
        ['phát triển', 'mở rộng', 'tiến bộ', 'nâng cao', 'tăng trưởng'],
        ['cải thiện', 'nâng cao', 'tiến bộ', 'sửa đổi', 'hoàn thiện'],
        ['người đi bộ', 'khách bộ hành', 'người đi đường']
      ];

      const areSynonyms = (a, b) => {
        const ca = stripPart(a);
        const cb = stripPart(b);
        return synGroups.some(g => {
          const inA = g.some(w => ca === w || ca.includes(w) || w.includes(ca));
          const inB = g.some(w => cb === w || cb.includes(w) || w.includes(cb));
          return inA && inB;
        });
      };

      const getVec = (str) => {
        const vec = {};
        const words = str.split(' ');
        words.forEach(w => { vec['w:' + w] = (vec['w:' + w] || 0) + 1.5; });
        for (let i = 0; i < words.length - 1; i++) {
          const bg = 'bg:' + words[i] + '_' + words[i+1];
          vec[bg] = (vec[bg] || 0) + 2.0;
        }
        const compact = str.replace(/\s+/g, '');
        for (let i = 0; i < compact.length - 2; i++) {
          const trigram = 'c:' + compact.slice(i, i + 3);
          vec[trigram] = (vec[trigram] || 0) + 1.0;
        }
        return vec;
      };

      const cosSim = (v1, v2) => {
        let dot = 0, n1 = 0, n2 = 0;
        for (let k in v1) {
          if (v2[k]) dot += v1[k] * v2[k];
          n1 += v1[k] * v1[k];
        }
        for (let k in v2) n2 += v2[k] * v2[k];
        return (n1 > 0 && n2 > 0) ? dot / (Math.sqrt(n1) * Math.sqrt(n2)) : 0;
      };

      const userVec = getVec(userNorm);
      let bestScore = 0;

      for (let sense of senses) {
        const senseCore = stripPart(sense);
        let score = 0;
        if (userNorm === sense || userCore === senseCore) {
          score = 1.0;
        } else if (userCore && (userCore.includes(senseCore) || senseCore.includes(userCore))) {
          score = Math.max(0.90, userCore.length / Math.max(senseCore.length, 1));
        } else if (areSynonyms(userNorm, sense)) {
          score = 0.92;
        } else {
          const sVec = getVec(sense);
          const cos = cosSim(userVec, sVec);
          const uTokens = new Set(userNorm.split(' '));
          const sTokens = new Set(sense.split(' '));
          let inter = 0;
          uTokens.forEach(t => { if (sTokens.has(t)) inter++; });
          const union = new Set([...uTokens, ...sTokens]).size;
          const jac = union > 0 ? inter / union : 0;
          score = (cos * 0.65) + (jac * 0.35);
        }
        if (score > bestScore) bestScore = score;
      }

      const isSimilar = bestScore >= threshold;
      const pct = Math.round(bestScore * 100);
      let feedback = '';
      if (bestScore >= 0.90) feedback = `Chính xác hoàn toàn! (${pct}%)`;
      else if (isSimilar) feedback = `Tương đồng ngữ nghĩa cao (${pct}% ➔ Đạt)`;
      else feedback = `Chưa sát nghĩa (Độ tương đồng: ${pct}%)`;

      return {
        is_similar: isSimilar,
        score: bestScore,
        percentage: pct,
        feedback: feedback
      };
    }

    function shuffleAndRestartQuiz() {
      if (!multiExCards || multiExCards.length === 0) return;
      multiExCards.sort(() => Math.random() - 0.5);
      const masks = ['mode1', 'mode2', 'mode3', 'mode4'];
      multiExCards.forEach(c => {
        c._assignedMask = masks[Math.floor(Math.random() * masks.length)];
      });
      multiExIndex = 0;
      multiExScore = { correct: 0, partial: 0, wrong: 0, total: multiExCards.length };
      renderMultiExCard();
    }

    async function initMultiExSession(forceReload = false) {
      try {
        if (!multiExCards || multiExCards.length === 0 || forceReload) {
          const badge = document.getElementById('multiExSourceBadge');
          if (badge) badge.textContent = 'Nguồn: Đang tải...';

          let cards = await apiRequest(`/api/reviews/due?language=${currentLearningLanguage}`);
          let sourceName = '';

          if (cards && cards.length > 0) {
            multiExCards = [...cards];
            sourceName = `Thẻ đến hạn (${cards.length})`;
          } else {
            const vocabRes = await apiRequest(`/api/vocab?language=${currentLearningLanguage}&limit=50`);
            const vocabCards = vocabRes.items || vocabRes || [];
            if (vocabCards.length > 0) {
              multiExCards = [...vocabCards];
              sourceName = `Kho từ vựng (${vocabCards.length})`;
            } else {
              multiExCards = [];
              sourceName = 'Chưa có từ vựng';
            }
          }

          if (badge) badge.textContent = `Nguồn: ${sourceName}`;
        }

        multiExCards.sort(() => Math.random() - 0.5);
        multiExIndex = 0;
        multiExScore = { correct: 0, partial: 0, wrong: 0, total: multiExCards.length };
        renderMultiExCard();
      } catch (err) {
        console.error("Error initializing multi-exercise session:", err);
      }
    }

    function renderMultiExCard() {
      const cardBox = document.getElementById('multiExCardBox');
      const completeBox = document.getElementById('multiExCompleteBox');
      const feedbackBox = document.getElementById('multiExFeedbackBox');
      const promptMain = document.getElementById('multiExPromptMain');
      const promptTitle = document.getElementById('multiExPromptTitle');
      const promptExtra = document.getElementById('multiExPromptExtra');
      const guideText = document.getElementById('multiExGuideText');
      const modeBadge = document.getElementById('multiExModeBadge');
      const wordInputContainer = document.getElementById('multiExWordInputContainer');
      const speakingContainer = document.getElementById('multiExSpeakingContainer');
      const meaningInputContainer = document.getElementById('multiExMeaningInputContainer');

      if (!multiExCards || multiExCards.length === 0) {
        promptTitle.textContent = 'THÔNG BÁO';
        promptMain.innerHTML = '<span class="text-sm font-semibold text-slate-400">Chưa có từ vựng nào trong danh sách. Hãy thêm từ mới hoặc nhập từ file CSV/Excel để bắt đầu ôn luyện.</span>';
        promptExtra.innerHTML = '';
        guideText.textContent = 'Hệ thống tự động đồng bộ từ vựng theo ngôn ngữ đang chọn.';
        wordInputContainer.classList.add('hidden');
        speakingContainer.classList.add('hidden');
        meaningInputContainer.classList.add('hidden');
        document.getElementById('btnMultiExCheck').classList.add('hidden');
        document.getElementById('btnMultiExReveal').classList.add('hidden');
        document.getElementById('btnMultiExNext').classList.add('hidden');
        return;
      }

      if (multiExIndex >= multiExCards.length) {
        completeBox.classList.remove('hidden');
        feedbackBox.classList.add('hidden');
        document.getElementById('multiExPromptTitle').parentElement.classList.add('hidden');
        wordInputContainer.classList.add('hidden');
        speakingContainer.classList.add('hidden');
        meaningInputContainer.classList.add('hidden');
        document.getElementById('btnMultiExCheck').classList.add('hidden');
        document.getElementById('btnMultiExReveal').classList.add('hidden');
        document.getElementById('btnMultiExNext').classList.add('hidden');
        document.getElementById('multiExCompleteStats').textContent = 
          `Bạn đã hoàn thành ${multiExCards.length} câu. Số câu chính xác: ${multiExScore.correct} / ${multiExCards.length} (${Math.round((multiExScore.correct / multiExCards.length) * 100)}%).`;
        return;
      }

      completeBox.classList.add('hidden');
      feedbackBox.classList.add('hidden');
      document.getElementById('multiExPromptTitle').parentElement.classList.remove('hidden');

      document.getElementById('btnMultiExCheck').classList.remove('hidden');
      document.getElementById('btnMultiExReveal').classList.remove('hidden');
      document.getElementById('btnMultiExNext').classList.add('hidden');

      // Reset inputs & speech state
      isMultiExChecked = false;
      isMultiExRevealed = false;
      document.getElementById('multiExWordInput').value = '';
      document.getElementById('multiExMeaningInput').value = '';
      multiExSpeechTranscript = '';
      multiExSpokenVerified = false;
      isMultiExListening = false;

      const micBtn = document.getElementById('btnMultiExMic');
      micBtn.className = 'px-4 py-2.5 bg-teal-600 hover:bg-teal-500 text-white rounded-xl text-xs font-bold transition flex items-center gap-2 shadow-lg shadow-teal-600/20';
      micBtn.innerHTML = '<i class="fa-solid fa-microphone"></i> <span>Bắt đầu đọc to / Thu âm</span>';

      const speechStatus = document.getElementById('multiExSpeechStatus');
      speechStatus.className = 'text-xs text-slate-400 pt-1';
      speechStatus.textContent = 'Chưa ghi âm giọng đọc. Bấm nút thu âm và đọc rõ từ vựng.';

      // Progress bar
      document.getElementById('multiExProgressText').textContent = `Câu ${multiExIndex + 1} / ${multiExCards.length}`;
      const pct = Math.round(((multiExIndex + 1) / multiExCards.length) * 100);
      document.getElementById('multiExProgressBar').style.width = `${pct}%`;

      const card = multiExCards[multiExIndex];
      const isChinese = (card.language === 'zh' || currentLearningLanguage === 'zh');
      document.getElementById('multiExLangTag').textContent = isChinese ? 'ZH' : 'EN';
      document.getElementById('multiExLangTag').className = isChinese
        ? 'px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20'
        : 'px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20';

      // Mode assignment
      if (multiExMode === 'mix') {
        const cycle = ['mode1', 'mode2', 'mode3', 'mode4'];
        currentActiveExerciseMode = card._assignedMask || cycle[multiExIndex % 4];
      } else {
        currentActiveExerciseMode = multiExMode;
      }

      const phonetic = isChinese 
        ? (card.language_specific_fields?.pinyin || card.pinyin || '') 
        : (card.ipa || card.language_specific_fields?.ipa || '');
      const pos = card.part_of_speech || (isChinese ? 'Hán tự' : 'từ vựng');

      if (currentActiveExerciseMode === 'mode1') {
        // Kiểu 1: Phiên âm -> Viết từ + Nghĩa TV
        modeBadge.className = 'px-3 py-1 rounded-xl text-xs font-bold bg-amber-500/15 text-amber-300 border border-amber-500/30 flex items-center gap-1.5';
        modeBadge.innerHTML = '<i class="fa-solid fa-headphones"></i> Kiểu 1: Phiên âm ➔ Viết từ + Ghi nghĩa TV';
        guideText.textContent = 'Dựa vào phiên âm và nghe âm thanh mẫu chuẩn, hãy tự gõ lại chính xác từ vựng và nhập nghĩa tiếng Việt tương ứng.';
        promptTitle.textContent = isChinese ? 'PHIÊN ÂM PINYIN CHUẨN XÁC' : 'PHIÊN ÂM IPA CHUẨN XÁC';
        promptMain.innerHTML = phonetic ? `<span class="font-mono text-amber-300">${phonetic}</span>` : `<span class="text-slate-400 text-2xl">[Nghe âm thanh mẫu chuẩn]</span>`;
        promptExtra.innerHTML = `
          <button onclick="playMultiExAudio()" class="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-semibold border border-slate-700 transition flex items-center gap-1.5 shadow-sm">
            <i class="fa-solid fa-volume-high text-emerald-400"></i> Nghe phát âm mẫu
          </button>
          <span class="text-xs px-2.5 py-1 rounded-lg bg-slate-800/80 text-slate-300 border border-slate-700 font-medium">${pos}</span>
        `;
        wordInputContainer.classList.remove('hidden');
        document.getElementById('multiExWordInputLabel').innerHTML = `<i class="fa-solid fa-keyboard text-cyan-400"></i> 1. Tự viết từ vựng (${isChinese ? 'chữ Hán' : 'tiếng Anh'}):`;
        document.getElementById('multiExWordInput').placeholder = isChinese ? 'Gõ chữ Hán chính xác...' : 'Gõ từ tiếng Anh chính xác...';
        speakingContainer.classList.add('hidden');
        meaningInputContainer.classList.remove('hidden');
        document.getElementById('multiExMeaningInputLabel').innerHTML = `<i class="fa-solid fa-pen text-teal-400"></i> 2. Tự ghi nghĩa tiếng Việt tương ứng:`;
        setTimeout(() => document.getElementById('multiExWordInput')?.focus(), 50);

      } else if (currentActiveExerciseMode === 'mode2') {
        // Kiểu 2: Từ vựng -> Đọc chuẩn + Ghi nghĩa TV
        modeBadge.className = 'px-3 py-1 rounded-xl text-xs font-bold bg-teal-500/15 text-teal-300 border border-teal-500/30 flex items-center gap-1.5';
        modeBadge.innerHTML = '<i class="fa-solid fa-microphone-lines"></i> Kiểu 2: Từ vựng ➔ Đọc chuẩn + Ghi nghĩa TV';
        guideText.textContent = 'Nhìn từ vựng hiển thị, bấm nút mic để đọc thật chuẩn xác qua microphone và nhập nghĩa tiếng Việt tương ứng.';
        promptTitle.textContent = isChinese ? 'CHỮ HÁN MỤC TIÊU' : 'TỪ TIẾNG ANH MỤC TIÊU';
        promptMain.innerHTML = `<span class="text-white">${card.term}</span>`;
        promptExtra.innerHTML = `
          <button onclick="playMultiExAudio()" class="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-semibold border border-slate-700 transition flex items-center gap-1.5 shadow-sm">
            <i class="fa-solid fa-volume-high text-emerald-400"></i> Nghe phát âm mẫu
          </button>
          <span class="text-xs px-2.5 py-1 rounded-lg bg-slate-800/80 text-slate-300 border border-slate-700 font-medium">${pos}</span>
        `;
        wordInputContainer.classList.add('hidden');
        speakingContainer.classList.remove('hidden');
        meaningInputContainer.classList.remove('hidden');
        document.getElementById('multiExMeaningInputLabel').innerHTML = `<i class="fa-solid fa-pen text-teal-400"></i> Tự ghi nghĩa tiếng Việt tương ứng:`;
        setTimeout(() => document.getElementById('multiExMeaningInput')?.focus(), 50);

      } else if (currentActiveExerciseMode === 'mode3') {
        // Kiểu 3: Nghĩa TV -> Đọc từ + Viết từ
        modeBadge.className = 'px-3 py-1 rounded-xl text-xs font-bold bg-indigo-500/15 text-indigo-300 border border-indigo-500/30 flex items-center gap-1.5';
        modeBadge.innerHTML = '<i class="fa-solid fa-pen-nib"></i> Kiểu 3: Nghĩa TV ➔ Đọc từ + Viết từ';
        guideText.textContent = 'Dựa vào nghĩa tiếng Việt, hãy bấm mic đọc to từ vựng và tự gõ lại chính xác từ đó.';
        promptTitle.textContent = 'ĐỊNH NGHĨA TIẾNG VIỆT';
        promptMain.innerHTML = `<span class="text-emerald-300 text-2xl sm:text-3xl font-bold">${card.definition}</span>`;
        promptExtra.innerHTML = `
          <button onclick="playMultiExAudio()" class="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-semibold border border-slate-700 transition flex items-center gap-1.5 shadow-sm">
            <i class="fa-solid fa-volume-high text-emerald-400"></i> Nghe âm thanh mẫu
          </button>
          <span class="text-xs px-2.5 py-1 rounded-lg bg-slate-800/80 text-slate-300 border border-slate-700 font-medium">${pos}</span>
        `;
        speakingContainer.classList.remove('hidden');
        wordInputContainer.classList.remove('hidden');
        document.getElementById('multiExWordInputLabel').innerHTML = `<i class="fa-solid fa-keyboard text-cyan-400"></i> Viết từ vựng (${isChinese ? 'chữ Hán' : 'tiếng Anh'}):`;
        document.getElementById('multiExWordInput').placeholder = isChinese ? 'Gõ chữ Hán chính xác...' : 'Gõ từ tiếng Anh chính xác...';
        meaningInputContainer.classList.add('hidden');
        setTimeout(() => document.getElementById('multiExWordInput')?.focus(), 50);

      } else if (currentActiveExerciseMode === 'mode4') {
        // Kiểu 4: Giấu ký tự (Cloze) ➔ Gõ từ hoàn chỉnh
        modeBadge.className = 'px-3 py-1 rounded-xl text-xs font-bold bg-purple-500/15 text-purple-300 border border-purple-500/30 flex items-center gap-1.5';
        modeBadge.innerHTML = '<i class="fa-solid fa-puzzle-piece"></i> Kiểu 4: Giấu ký tự (Cloze) ➔ Gõ từ hoàn chỉnh';
        guideText.textContent = 'Hệ thống đã giấu một số chữ cái. Dựa vào các chữ cái còn lại và nghĩa tiếng Việt, hãy gõ từ hoàn chỉnh.';
        promptTitle.textContent = isChinese ? 'CHỮ BỊ GIẤU & NGHĨA' : 'TỪ BỊ GIẤU KÝ TỰ & NGHĨA';
        const clozeTerm = makeCloze(card.term);
        promptMain.innerHTML = `<span class="font-mono text-cyan-300 text-2xl sm:text-3xl tracking-widest font-bold">${clozeTerm}</span>`;
        promptExtra.innerHTML = `
          <button onclick="playMultiExAudio()" class="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-semibold border border-slate-700 transition flex items-center gap-1.5 shadow-sm">
            <i class="fa-solid fa-volume-high text-emerald-400"></i> Nghe âm thanh
          </button>
          <div class="text-xs px-2.5 py-1 rounded-lg bg-slate-800/80 text-emerald-300 border border-slate-700 font-medium">Nghĩa: ${card.definition}</div>
          <span class="text-xs px-2.5 py-1 rounded-lg bg-slate-800/80 text-slate-300 border border-slate-700 font-medium">${pos}</span>
        `;
        speakingContainer.classList.add('hidden');
        wordInputContainer.classList.remove('hidden');
        document.getElementById('multiExWordInputLabel').innerHTML = `<i class="fa-solid fa-keyboard text-cyan-400"></i> Gõ từ vựng hoàn chỉnh (${isChinese ? 'chữ Hán' : 'tiếng Anh'}):`;
        document.getElementById('multiExWordInput').placeholder = isChinese ? 'Gõ chữ Hán hoàn chỉnh...' : 'Gõ từ tiếng Anh hoàn chỉnh...';
        meaningInputContainer.classList.add('hidden');
        setTimeout(() => document.getElementById('multiExWordInput')?.focus(), 50);
      }
    }

    function playMultiExAudio() {
      if (!multiExCards || !multiExCards[multiExIndex]) return;
      const card = multiExCards[multiExIndex];
      speakText(card.term, card.language || currentLearningLanguage);
    }

    function toggleMultiExMic() {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) {
        alert('Trình duyệt của bạn chưa hỗ trợ Web Speech API. Bạn có thể sử dụng nút "Đã tự đọc to" để hoàn thành bài đọc.');
        return;
      }

      if (isMultiExListening && multiExRecognition) {
        try { multiExRecognition.stop(); } catch(e) {}
        isMultiExListening = false;
        return;
      }

      const card = multiExCards[multiExIndex];
      const isChinese = (card.language === 'zh' || currentLearningLanguage === 'zh');
      const micBtn = document.getElementById('btnMultiExMic');
      const statusEl = document.getElementById('multiExSpeechStatus');

      try {
        multiExRecognition = new SpeechRecognition();
        multiExRecognition.lang = isChinese ? 'zh-CN' : 'en-US';
        multiExRecognition.interimResults = false;
        multiExRecognition.maxAlternatives = 3;

        micBtn.className = 'px-4 py-2.5 bg-rose-600 animate-pulse text-white rounded-xl text-xs font-bold transition flex items-center gap-2 shadow-lg shadow-rose-600/30';
        micBtn.innerHTML = '<i class="fa-solid fa-microphone-lines"></i> <span>Đang nghe... Hãy đọc to</span>';
        statusEl.className = 'text-xs text-amber-300 font-medium pt-1';
        statusEl.textContent = 'Đang lắng nghe... Vui lòng đọc rõ từ vựng.';
        isMultiExListening = true;

        multiExRecognition.onresult = (event) => {
          isMultiExListening = false;
          micBtn.className = 'px-4 py-2.5 bg-teal-600 hover:bg-teal-500 text-white rounded-xl text-xs font-bold transition flex items-center gap-2 shadow-lg shadow-teal-600/20';
          micBtn.innerHTML = '<i class="fa-solid fa-microphone"></i> <span>Bắt đầu đọc to / Thu âm</span>';

          const results = Array.from(event.results[0]).map(r => r.transcript.trim());
          const transcript = results[0] || '';
          multiExSpeechTranscript = transcript;

          const cleanTarget = card.term.toLowerCase().replace(/[.,/#!$%^&*;:{}=\-_`~()]/g, "").trim();

          const isMatch = results.some(t => {
            const c = t.toLowerCase().replace(/[.,/#!$%^&*;:{}=\-_`~()]/g, "").trim();
            return c === cleanTarget || c.includes(cleanTarget) || cleanTarget.includes(c);
          });

          if (isMatch) {
            multiExSpokenVerified = true;
            statusEl.className = 'text-xs text-emerald-400 font-bold pt-1';
            statusEl.innerHTML = `<i class="fa-solid fa-circle-check"></i> Phát âm chuẩn xác: "${transcript}"`;
          } else {
            statusEl.className = 'text-xs text-amber-300 font-medium pt-1';
            statusEl.innerHTML = `<i class="fa-solid fa-circle-exclamation"></i> Đã nghe thấy: "${transcript}" (Từ chuẩn: "${card.term}"). Bạn có thể thử lại hoặc bấm "Đã tự đọc to".`;
          }
        };

        multiExRecognition.onerror = (e) => {
          isMultiExListening = false;
          micBtn.className = 'px-4 py-2.5 bg-teal-600 hover:bg-teal-500 text-white rounded-xl text-xs font-bold transition flex items-center gap-2 shadow-lg shadow-teal-600/20';
          micBtn.innerHTML = '<i class="fa-solid fa-microphone"></i> <span>Bắt đầu đọc to / Thu âm</span>';
          statusEl.className = 'text-xs text-rose-400 font-medium pt-1';
          statusEl.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> Chưa bắt được giọng đọc. Hãy kiểm tra microphone hoặc bấm "Đã tự đọc to".';
        };

        multiExRecognition.onend = () => {
          isMultiExListening = false;
          micBtn.className = 'px-4 py-2.5 bg-teal-600 hover:bg-teal-500 text-white rounded-xl text-xs font-bold transition flex items-center gap-2 shadow-lg shadow-teal-600/20';
          micBtn.innerHTML = '<i class="fa-solid fa-microphone"></i> <span>Bắt đầu đọc to / Thu âm</span>';
        };

        multiExRecognition.start();
      } catch (err) {
        isMultiExListening = false;
        micBtn.className = 'px-4 py-2.5 bg-teal-600 hover:bg-teal-500 text-white rounded-xl text-xs font-bold transition flex items-center gap-2 shadow-lg shadow-teal-600/20';
        micBtn.innerHTML = '<i class="fa-solid fa-microphone"></i> <span>Bắt đầu đọc to / Thu âm</span>';
        statusEl.className = 'text-xs text-rose-400 pt-1';
        statusEl.innerHTML = 'Không thể khởi động Web Speech API. Bạn có thể sử dụng nút "Đã tự đọc to".';
      }
    }

    function markMultiExSpoken() {
      multiExSpokenVerified = true;
      const statusEl = document.getElementById('multiExSpeechStatus');
      statusEl.className = 'text-xs text-emerald-400 font-bold pt-1';
      statusEl.innerHTML = '<i class="fa-solid fa-circle-check"></i> Đã ghi nhận: Bạn đã tự đọc to chuẩn xác!';
    }

    async function checkMultiExAnswer() {
      if (!multiExCards || !multiExCards[multiExIndex]) return;
      const card = multiExCards[multiExIndex];
      const isChinese = (card.language === 'zh' || currentLearningLanguage === 'zh');
      isMultiExChecked = true;

      const userWord = (document.getElementById('multiExWordInput')?.value || '').trim();
      const userMeaning = (document.getElementById('multiExMeaningInput')?.value || '').trim();

      const cleanStr = (s) => (s || '').toLowerCase().replace(/[.,/#!$%^&*;:{}=\-_`~()?]/g, "").trim();

      const targetWordClean = cleanStr(card.term);
      const userWordClean = cleanStr(userWord);

      let wordCorrect = false;
      let speechCorrect = false;
      let meaningCorrect = false;

      const meaningEval = (currentActiveExerciseMode === 'mode1' || currentActiveExerciseMode === 'mode2')
        ? evaluateVietnameseMeaningSimilarity(userMeaning, card.definition, 0.52)
        : { is_similar: true, score: 1.0, percentage: 100, feedback: '' };

      if (currentActiveExerciseMode === 'mode1') {
        wordCorrect = (userWordClean === targetWordClean);
        meaningCorrect = meaningEval.is_similar;
        speechCorrect = true;
      } else if (currentActiveExerciseMode === 'mode2') {
        wordCorrect = true;
        speechCorrect = multiExSpokenVerified;
        meaningCorrect = meaningEval.is_similar;
      } else if (currentActiveExerciseMode === 'mode3') {
        wordCorrect = (userWordClean === targetWordClean);
        speechCorrect = multiExSpokenVerified;
        meaningCorrect = true;
      } else if (currentActiveExerciseMode === 'mode4') {
        wordCorrect = (userWordClean === targetWordClean);
        speechCorrect = true;
        meaningCorrect = true;
      }

      let allCorrect = false;
      if (!isMultiExRevealed) {
        if (currentActiveExerciseMode === 'mode1') allCorrect = wordCorrect && meaningCorrect;
        else if (currentActiveExerciseMode === 'mode2') allCorrect = speechCorrect && meaningCorrect;
        else if (currentActiveExerciseMode === 'mode3') allCorrect = wordCorrect && speechCorrect;
        else if (currentActiveExerciseMode === 'mode4') allCorrect = wordCorrect;
      }

      if (allCorrect) {
        multiExScore.correct++;
      } else {
        multiExScore.wrong++;
        // Tự động xếp thẻ bị sai hoặc chưa thuộc vào cuối bài để kiểm tra lại
        multiExCards.push(card);
        multiExScore.total = multiExCards.length;
        document.getElementById('multiExProgressText').textContent = `Câu ${multiExIndex + 1} / ${multiExCards.length}`;
        const pct = Math.round(((multiExIndex + 1) / multiExCards.length) * 100);
        document.getElementById('multiExProgressBar').style.width = `${pct}%`;
      }

      const feedbackBox = document.getElementById('multiExFeedbackBox');
      feedbackBox.classList.remove('hidden');

      const statusAlert = document.getElementById('multiExStatusAlert');
      const vocabIdForHist = card.vocab_id || card.id;
      if (allCorrect) {
        statusAlert.className = 'p-4 rounded-xl border border-emerald-500/30 bg-emerald-500/10 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs';
        statusAlert.innerHTML = `
          <div class="flex items-center gap-3">
            <i class="fa-solid fa-circle-check text-emerald-400 text-xl"></i>
            <div>
              <div class="font-bold text-emerald-300 text-sm">✅ ĐÃ THUỘC — Trả lời hoàn toàn chính xác! 🎉</div>
              <div class="text-slate-300 text-[11px] mt-0.5">Từ vựng đã được củng cố và bước lên nấc chu kỳ tiếp theo trong trí nhớ dài hạn.</div>
            </div>
          </div>
          <button onclick="openVocabHistoryModal('${vocabIdForHist}')" class="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-emerald-300 rounded-lg text-xs font-semibold border border-slate-700 transition flex items-center gap-1.5 shrink-0 self-start sm:self-auto shadow-sm">
            <i class="fa-solid fa-clock-rotate-left"></i> Xem lịch sử học
          </button>
        `;
      } else {
        statusAlert.className = 'p-4 rounded-xl border border-rose-500/30 bg-rose-500/10 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs';
        statusAlert.innerHTML = `
          <div class="flex items-center gap-3">
            <i class="fa-solid fa-circle-xmark text-rose-400 text-xl"></i>
            <div>
              <div class="font-bold text-rose-300 text-sm">❌ CHƯA THUỘC — Tự động xếp vào cuối bài để ôn lại!</div>
              <div class="text-slate-300 text-[11px] mt-0.5">Hệ thống đã ghi nhận trạng thái <strong>Chưa thuộc</strong> vào lịch sử học SRS và đưa từ này vào cuối danh sách bài để bạn làm lại cho tới khi thuộc.</div>
            </div>
          </div>
          <button onclick="openVocabHistoryModal('${vocabIdForHist}')" class="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-rose-300 rounded-lg text-xs font-semibold border border-slate-700 transition flex items-center gap-1.5 shrink-0 self-start sm:self-auto shadow-sm">
            <i class="fa-solid fa-clock-rotate-left"></i> Xem lịch sử học
          </button>
        `;
      }

      document.getElementById('feedbackTermText').textContent = card.term;
      document.getElementById('feedbackPosTag').textContent = card.part_of_speech || (isChinese ? 'Hán tự' : 'từ');
      const phonetic = isChinese 
        ? (card.language_specific_fields?.pinyin || card.pinyin || '') 
        : (card.ipa || card.language_specific_fields?.ipa || '');
      document.getElementById('feedbackPhoneticText').textContent = phonetic ? phonetic : '';

      const wordComp = document.getElementById('feedbackWordUserComparison');
      if (currentActiveExerciseMode === 'mode1' || currentActiveExerciseMode === 'mode3' || currentActiveExerciseMode === 'mode4') {
        if (wordCorrect) {
          wordComp.innerHTML = `<span class="text-emerald-400 font-semibold"><i class="fa-solid fa-check"></i> Bạn đã viết: "${userWord}" (Chính xác)</span>`;
        } else {
          wordComp.innerHTML = `<span class="text-rose-400 font-semibold"><i class="fa-solid fa-xmark"></i> Bạn đã viết: "${userWord || '(trống)'}"</span> <span class="text-slate-400">➔ Từ chuẩn: <strong class="text-white">${card.term}</strong></span>`;
        }
      } else {
        if (speechCorrect) {
          wordComp.innerHTML = `<span class="text-emerald-400 font-semibold"><i class="fa-solid fa-check"></i> Phát âm: Chuẩn xác</span>`;
        } else {
          wordComp.innerHTML = `<span class="text-amber-300 font-semibold"><i class="fa-solid fa-info"></i> Phát âm: Cần luyện đọc to từ "${card.term}"</span>`;
        }
      }

      document.getElementById('feedbackMeaningText').textContent = card.definition;
      const meaningComp = document.getElementById('feedbackMeaningUserComparison');
      if (currentActiveExerciseMode === 'mode1' || currentActiveExerciseMode === 'mode2') {
        if (!userMeaning) {
          meaningComp.innerHTML = `<span class="text-rose-400 font-semibold"><i class="fa-solid fa-xmark"></i> Bạn chưa nhập nghĩa tiếng Việt</span> <span class="text-slate-400">➔ Nghĩa chuẩn: <strong class="text-white">${card.definition}</strong></span>`;
        } else if (meaningEval.is_similar) {
          const badgeColor = meaningEval.percentage >= 90 ? 'text-emerald-400' : 'text-teal-300';
          meaningComp.innerHTML = `
            <span class="${badgeColor} font-semibold">
              <i class="fa-solid fa-circle-nodes"></i> ${meaningEval.feedback}
            </span>
            <span class="text-slate-300"> — Bạn ghi: "<strong class="text-white">${userMeaning}</strong>"</span>
            <span class="text-slate-400"> (Nghĩa mẫu: <strong class="text-slate-200">${card.definition}</strong>)</span>
          `;
        } else {
          meaningComp.innerHTML = `
            <span class="text-rose-400 font-semibold">
              <i class="fa-solid fa-circle-xmark"></i> ${meaningEval.feedback}
            </span>
            <span class="text-slate-400"> — Bạn ghi: "<span class="text-rose-300">${userMeaning}</span>" ➔ Nghĩa chuẩn: <strong class="text-white">${card.definition}</strong></span>
          `;
        }
      } else {
        meaningComp.innerHTML = `<span class="text-slate-400">Đề bài gợi ý theo nghĩa tiếng Việt này</span>`;
      }

      const extraBox = document.getElementById('feedbackExtraContextBox');
      const rootRow = document.getElementById('feedbackRootWordRow');
      const exRow = document.getElementById('feedbackExamplesRow');
      const exList = document.getElementById('feedbackExamplesList');
      exList.innerHTML = '';

      let hasExtra = false;
      if (card.root_word) {
        rootRow.classList.remove('hidden');
        document.getElementById('feedbackRootWordVal').textContent = card.root_word;
        hasExtra = true;
      } else {
        rootRow.classList.add('hidden');
      }

      if (card.examples && card.examples.length > 0) {
        exRow.classList.remove('hidden');
        card.examples.forEach(ex => {
          const li = document.createElement('li');
          li.textContent = ex;
          exList.appendChild(li);
        });
        hasExtra = true;
      } else {
        exRow.classList.add('hidden');
      }

      if (hasExtra) {
        extraBox.classList.remove('hidden');
      } else {
        extraBox.classList.add('hidden');
      }

      document.getElementById('btnMultiExCheck').classList.add('hidden');
      document.getElementById('btnMultiExReveal').classList.add('hidden');
      document.getElementById('btnMultiExNext').classList.remove('hidden');

      try {
        await apiRequest('/api/practice/submit', {
          method: 'POST',
          body: JSON.stringify({
            practice_type: `multimodal_${currentActiveExerciseMode}`,
            vocab_id: card.vocab_id || card.id,
            prompt: `${card.term} (${phonetic}) - ${card.definition}`,
            user_text: `Từ: ${userWord || card.term} | Đọc: ${speechCorrect ? 'Chuẩn' : 'Chưa'} | Nghĩa: ${userMeaning || card.definition}`,
            model_answer: `${card.term} - ${card.definition}`,
            self_assessment_score: allCorrect ? 4 : 1,
            is_correct: allCorrect
          })
        });
      } catch (err) {
        console.error("Error saving practice submission:", err);
      }
    }

    function revealMultiExAnswer() {
      isMultiExRevealed = true;
      const card = multiExCards[multiExIndex];
      if (!card) return;
      document.getElementById('multiExWordInput').value = card.term;
      document.getElementById('multiExMeaningInput').value = card.definition;
      checkMultiExAnswer();
    }

    function nextMultiExCard() {
      isMultiExRevealed = false;
      multiExIndex++;
      renderMultiExCard();
    }

    // Keydown listener for Enter key in review exercises
    document.addEventListener('keydown', (e) => {
      if (currentView === 'reviews' && reviewActiveSubTab === 'exercises') {
        if (e.key === 'Enter') {
          const activeEl = document.activeElement;
          const isInput = (activeEl && (activeEl.id === 'multiExWordInput' || activeEl.id === 'multiExMeaningInput'));
          if (isInput || isMultiExChecked) {
            e.preventDefault();
            if (!isMultiExChecked) {
              checkMultiExAnswer();
            } else {
              nextMultiExCard();
            }
          }
        }
      }
    });

    // REVIEW CENTER VIEW (Main Loader)
    async function loadReviewCenterView() {
      try {
        const cards = await apiRequest(`/api/reviews/due?language=${currentLearningLanguage}`);
        document.getElementById('reviewDueCount').textContent = cards.length;
        const list = document.getElementById('reviewDueCardsList');
        list.innerHTML = '';
        if (cards.length === 0) {
          list.innerHTML = '<div class="text-xs text-slate-500 py-4 text-center">Không có thẻ nào đến hạn ôn tập hôm nay! Bạn đã hoàn thành xuất sắc!</div>';
        } else {
          cards.slice(0, 15).forEach(c => {
            const row = document.createElement('div');
            row.className = "flex items-center justify-between p-3 rounded-xl bg-slate-950/60 border border-slate-800 text-xs";
            const phonetic = (c.language === 'zh' || currentLearningLanguage === 'zh')
              ? (c.language_specific_fields?.pinyin || c.pinyin || '')
              : (c.ipa || c.language_specific_fields?.ipa || '');
            row.innerHTML = `
              <div>
                <strong class="text-white">${c.term}</strong>
                <span class="text-slate-400 ml-2 font-mono">${phonetic}</span>
                <div class="text-[11px] text-slate-400 mt-0.5">${c.definition}</div>
              </div>
              <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20">Đến hạn</span>
            `;
            list.appendChild(row);
          });
        }

        try {
          const prog = await apiRequest(`/api/progress?language=${currentLearningLanguage}`);
          if (prog && prog.learned_cards !== undefined) {
            document.getElementById('reviewMasteredCount').textContent = prog.learned_cards;
          }
        } catch (e) {}

        initMultiExSession();
      } catch (err) {
        console.error("Error in loadReviewCenterView:", err);
      }
    }

    // VOCABULARY STUDY HISTORY MODAL
    async function openVocabHistoryModal(vocabId) {
      if (!vocabId) return;
      try {
        const modal = document.getElementById('modalVocabHistory');
        if (!modal) return;
        modal.classList.remove('hidden');

        document.getElementById('histModalTerm').textContent = 'Đang tải...';
        document.getElementById('histModalPos').textContent = '';
        document.getElementById('histModalPhonetic').textContent = '';
        document.getElementById('histModalDefinition').textContent = '';
        document.getElementById('histModalTotalAttempts').textContent = '-';
        document.getElementById('histModalCorrectCount').textContent = '-';
        document.getElementById('histModalIncorrectCount').textContent = '-';
        document.getElementById('histModalNextInterval').textContent = '-';
        document.getElementById('histModalRetentionRate').textContent = '0%';
        document.getElementById('histModalRetentionBar').style.width = '0%';
        const listEl = document.getElementById('histModalTimelineList');
        listEl.innerHTML = '<div class="text-xs text-slate-400 py-4 text-center"><i class="fa-solid fa-spinner fa-spin mr-2"></i>Đang tải dữ liệu lịch sử...</div>';

        const data = await apiRequest(`/api/vocab/${vocabId}/history`);
        const s = data.srs_card || {};
        const logs = data.history || [];

        const isZh = (data.language === 'zh' || data.vocab?.language === 'zh');
        const phonetic = isZh 
          ? (data.pinyin || data.vocab?.pinyin || data.language_specific_fields?.pinyin || '') 
          : (data.ipa || data.vocab?.ipa || data.language_specific_fields?.ipa || '');

        document.getElementById('histModalTerm').textContent = data.term || data.vocab?.term || 'Từ vựng';
        document.getElementById('histModalPos').textContent = data.part_of_speech || data.vocab?.part_of_speech || (isZh ? 'Hán tự' : 'từ');
        document.getElementById('histModalPhonetic').textContent = phonetic ? `[${phonetic}]` : '';
        document.getElementById('histModalDefinition').textContent = data.definition || data.vocab?.definition || '';

        const totalAttempts = data.total_attempts ?? data.metrics?.total_attempts ?? logs.length;
        const correctAttempts = data.correct_count ?? data.correct_attempts ?? data.metrics?.correct_attempts ?? 0;
        const incorrectAttempts = data.incorrect_count ?? data.incorrect_attempts ?? data.metrics?.incorrect_attempts ?? 0;
        const nextInterval = (s.interval_days !== undefined ? s.interval_days : (logs[0]?.card_interval || 1));

        document.getElementById('histModalTotalAttempts').textContent = totalAttempts;
        document.getElementById('histModalCorrectCount').textContent = correctAttempts;
        document.getElementById('histModalIncorrectCount').textContent = incorrectAttempts;
        document.getElementById('histModalNextInterval').textContent = nextInterval + ' ngày';

        const rate = data.retention_rate !== undefined ? data.retention_rate : (data.metrics?.retention_rate ?? 0);
        document.getElementById('histModalRetentionRate').textContent = `${rate}%`;
        document.getElementById('histModalRetentionBar').style.width = `${rate}%`;

        listEl.innerHTML = '';
        if (logs.length === 0) {
          listEl.innerHTML = '<div class="text-xs text-slate-500 py-4 text-center">Chưa có lượt học nào được ghi lại cho từ này. Hãy bắt đầu ôn tập ngay!</div>';
        } else {
          logs.forEach(log => {
            const isCorrect = log.is_correct;
            const badgeClass = isCorrect
              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
              : 'bg-rose-500/10 text-rose-400 border-rose-500/20';
            const badgeText = isCorrect ? 'ĐÃ THUỘC' : 'CHƯA THUỘC';
            const badgeIcon = isCorrect ? 'fa-check' : 'fa-xmark';

            const row = document.createElement('div');
            row.className = 'p-3 rounded-xl bg-slate-950/70 border border-slate-800 text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-2';
            row.innerHTML = `
              <div class="space-y-0.5">
                <div class="flex items-center gap-2">
                  <span class="px-2 py-0.5 rounded text-[10px] font-bold border ${badgeClass} flex items-center gap-1">
                    <i class="fa-solid ${badgeIcon}"></i> ${badgeText}
                  </span>
                  <span class="text-[11px] text-slate-300 font-medium">Hình thức: ${log.practice_type || 'SRS Review'}</span>
                  ${log.rating ? `<span class="text-[10px] text-slate-500">(Đánh giá: ${log.rating}/5)</span>` : ''}
                </div>
                ${log.user_text ? `<div class="text-[11px] text-slate-400">Ghi nhận: <span class="text-slate-200">${log.user_text}</span></div>` : ''}
              </div>
              <div class="text-[10px] text-slate-500 shrink-0">
                ${(log.created_at || '').replace('T', ' ').slice(0, 16)}
              </div>
            `;
            listEl.appendChild(row);
          });
        }
      } catch (err) {
        alert('Lỗi tải lịch sử học: ' + err.message);
      }
    }

    // SRS RE-LEARNING CENTER DATA & SESSION
    async function loadRelearnCenterData() {
      try {
        const dist = await apiRequest(`/api/srs/distribution?language=${currentLearningLanguage}`);
        if (dist) {
          document.getElementById('relearnBox1').textContent = dist.box_1_day ?? dist.boxes?.box_1 ?? 0;
          document.getElementById('relearnBox2').textContent = dist.box_3_days ?? dist.boxes?.box_2 ?? 0;
          document.getElementById('relearnBox3').textContent = dist.box_7_days ?? dist.boxes?.box_3 ?? 0;
          document.getElementById('relearnBox4').textContent = dist.box_14_days ?? dist.boxes?.box_4 ?? 0;
          document.getElementById('relearnBox5').textContent = dist.box_30_plus_days ?? dist.boxes?.box_5 ?? 0;
          document.getElementById('relearnLapsedBadgeCount').textContent = dist.lapsed_count ?? 0;
        }

        const lapsedList = await apiRequest(`/api/srs/lapsed?language=${currentLearningLanguage}&limit=50`);
        const container = document.getElementById('relearnLapsedCardsList');
        if (!container) return;
        container.innerHTML = '';

        if (!lapsedList || lapsedList.length === 0) {
          container.innerHTML = '<div class="text-xs text-slate-500 py-4 text-center">Không có từ nào bị đánh dấu "Chưa thuộc" hoặc hay quên. Trí nhớ của bạn đang rất tuyệt vời!</div>';
          return;
        }

        lapsedList.forEach(card => {
          const isZh = (card.language === 'zh' || currentLearningLanguage === 'zh');
          const phonetic = isZh ? (card.language_specific_fields?.pinyin || card.pinyin || '') : (card.ipa || card.language_specific_fields?.ipa || '');
          const row = document.createElement('div');
          row.className = 'flex items-center justify-between p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 text-xs hover:border-slate-700 transition';
          row.innerHTML = `
            <div class="space-y-0.5">
              <div class="flex items-center gap-2">
                <strong class="text-white text-sm">${card.term}</strong>
                ${phonetic ? `<span class="text-amber-300 font-mono text-xs">[${phonetic}]</span>` : ''}
                <span class="px-2 py-0.5 rounded text-[9px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20">
                  <i class="fa-solid fa-triangle-exclamation mr-1"></i>Quên ${card.lapses || 1} lần
                </span>
                <span class="px-1.5 py-0.5 rounded text-[9px] font-semibold bg-slate-800 text-slate-400 border border-slate-700 uppercase">
                  ${card.state || 'RELEARNING'}
                </span>
              </div>
              <div class="text-[11px] text-slate-400">${card.definition}</div>
            </div>
            <div class="flex items-center gap-2 shrink-0">
              <button onclick="openVocabHistoryModal('${card.vocab_id || card.id}')" title="Xem lịch sử học" class="p-2 text-slate-400 hover:text-cyan-300 bg-slate-800/80 hover:bg-slate-800 rounded-lg border border-slate-700 transition text-xs flex items-center gap-1.5">
                <i class="fa-solid fa-clock-rotate-left"></i> <span class="hidden sm:inline">Lịch sử</span>
              </button>
            </div>
          `;
          container.appendChild(row);
        });
      } catch (err) {
        console.error("Error loading relearn center data:", err);
      }
    }

    async function startLapsedRelearnSession() {
      try {
        const res = await apiRequest('/api/sessions/start', {
          method: 'POST',
          body: JSON.stringify({
            session_type: 'srs_relearn',
            learning_language: currentLearningLanguage,
            unlimited: true
          })
        });
        currentSession = res.session;
        currentCard = res.current_card;
        if (!currentCard || res.session.total_cards === 0) {
          alert('Không có từ nào thuộc danh sách cần học lại trong không gian ngôn ngữ này! Bạn đã nhớ hết các từ rồi.');
          return;
        }
        openActiveSessionUI();
      } catch (err) {
        alert(err.message);
      }
    }

    // PRACTICE VIEW
    async function loadPracticeView() {
      try {
        const submissions = await apiRequest('/api/practice/history');
        const container = document.getElementById('practiceHistoryTable');
        container.innerHTML = '';
        if (submissions.length === 0) {
          container.innerHTML = '<div class="text-xs text-slate-500 py-2">Chưa có bài tập thực hành nào được lưu.</div>';
          return;
        }

        submissions.forEach(sub => {
          const d = document.createElement('div');
          d.className = "p-3 rounded-xl bg-slate-950/60 border border-slate-800 text-xs flex items-center justify-between";
          d.innerHTML = `
            <div>
              <div class="font-bold text-white">${sub.vocab_term || 'Bài luyện tập'}: "${sub.user_text}"</div>
              <div class="text-[10px] text-slate-400 mt-0.5">Loại: ${sub.practice_type} • Điểm: ${sub.self_assessment_score}/5</div>
            </div>
            <span class="text-[10px] text-slate-500">${sub.created_at.slice(0, 10)}</span>
          `;
          container.appendChild(d);
        });
      } catch (err) {
        console.error(err);
      }
    }

    function revealPracticeModelAnswer() {
      document.getElementById('practiceModelBox').classList.toggle('hidden');
    }

    async function submitPracticeWriting() {
      const text = document.getElementById('practiceUserInput').value.trim();
      if (!text) return alert('Vui lòng nhập câu của bạn');
      try {
        await apiRequest('/api/practice/submit', {
          method: 'POST',
          body: JSON.stringify({
            practice_type: 'sentence_writing',
            prompt: document.getElementById('practicePromptText').textContent,
            user_text: text,
            model_answer: document.getElementById('practiceModelAnswerText').textContent,
            self_assessment_score: 5
          })
        });
        alert('Đã lưu bài thực hành viết câu thành công!');
        document.getElementById('practiceUserInput').value = '';
        loadPracticeView();
      } catch (e) {
        alert(e.message);
      }
    }

    function playPracticeTTS() {
      speakText('resilient', 'en');
    }

    function toggleSpeechRecording() {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) {
        return alert('Trình duyệt của bạn chưa hỗ trợ Web Speech Recognition API.');
      }
      const recognition = new SpeechRecognition();
      recognition.lang = currentLearningLanguage === 'zh' ? 'zh-CN' : 'en-US';
      const btn = document.getElementById('speechRecBtn');
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang nghe...';

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        document.getElementById('speechResultBox').classList.remove('hidden');
        document.getElementById('speechResultText').textContent = transcript;
        btn.innerHTML = '<i class="fa-solid fa-microphone"></i> Bắt đầu nói';
      };
      recognition.onerror = () => {
        btn.innerHTML = '<i class="fa-solid fa-microphone"></i> Bắt đầu nói';
      };
      recognition.start();
    }

    // IMPORTER WIZARD
    function switchImportTab(mode) {
      const isFile = mode === 'file';
      document.getElementById('importTabFile').className = isFile 
        ? 'pb-3 px-4 text-xs font-bold border-b-2 border-emerald-500 text-emerald-400' 
        : 'pb-3 px-4 text-xs font-bold border-b-2 border-transparent text-slate-400 hover:text-white';
      document.getElementById('importTabPaste').className = !isFile 
        ? 'pb-3 px-4 text-xs font-bold border-b-2 border-emerald-500 text-emerald-400' 
        : 'pb-3 px-4 text-xs font-bold border-b-2 border-transparent text-slate-400 hover:text-white';

      document.getElementById('importFileSection').classList.toggle('hidden', !isFile);
      document.getElementById('importPasteSection').classList.toggle('hidden', isFile);
    }

    async function loadImporterView() {
      const decks = await apiRequest(`/api/decks?language=${currentLearningLanguage}`);
      const sel = document.getElementById('importTargetDeck');
      sel.innerHTML = '';
      decks.forEach(d => {
        sel.innerHTML += `<option value="${d.id}">${d.name} (${d.target_language})</option>`;
      });
    }

    function handleWizardFileSelected(e) {
      if (e.target.files && e.target.files[0]) {
        selectedWizardFile = e.target.files[0];
        const lbl = document.getElementById('selectedFileName');
        lbl.textContent = `Tệp đã chọn: ${selectedWizardFile.name}`;
        lbl.classList.remove('hidden');
      }
    }

    async function previewImportData() {
      const deckId = document.getElementById('importTargetDeck').value;
      if (!deckId) return alert('Vui lòng chọn hoặc tạo bộ thẻ đích');

      try {
        let previewData;
        const isFile = !document.getElementById('importFileSection').classList.contains('hidden');
        if (isFile) {
          if (!selectedWizardFile) return alert('Vui lòng chọn tệp CSV hoặc Excel');
          const formData = new FormData();
          formData.append('file', selectedWizardFile);
          previewData = await apiRequest(`/api/decks/${deckId}/import/preview`, {
            method: 'POST',
            body: formData,
            isFormData: true
          });
        } else {
          const text = document.getElementById('wizardPasteInput').value.trim();
          if (!text) return alert('Vui lòng dán dữ liệu vào ô');
          const blob = new Blob([text], { type: 'text/tab-separated-values' });
          const formData = new FormData();
          formData.append('file', blob, 'paste.tsv');
          previewData = await apiRequest(`/api/decks/${deckId}/import/preview`, {
            method: 'POST',
            body: formData,
            isFormData: true
          });
        }

        renderImportPreview(previewData);
      } catch (err) {
        alert(err.message);
      }
    }

    function renderImportPreview(data) {
      const area = document.getElementById('importPreviewArea');
      area.classList.remove('hidden');
      document.getElementById('previewCountBadge').textContent = `${data.total_rows} hàng phát hiện`;

      const m = data.column_mapping || {};
      const badges = document.getElementById('importMappingBadges');
      badges.innerHTML = `
        <span class="text-slate-400 font-semibold self-center">Cột nhận diện:</span>
        <span class="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">Từ: <b>${m.term || '—'}</b></span>
        <span class="px-2 py-0.5 rounded ${m.ipa ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'}">Phiên âm: <b>${m.ipa || 'Chưa nhận diện'}</b></span>
        <span class="px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20">Định nghĩa: <b>${m.definition || '—'}</b></span>
        <span class="px-2 py-0.5 rounded bg-teal-500/10 text-teal-400 border border-teal-500/20">Loại từ: <b>${m.part_of_speech || '—'}</b></span>
      `;

      const tbody = document.getElementById('previewTableBody');
      tbody.innerHTML = '';
      (data.preview_rows || []).slice(0, 15).forEach(r => {
        const tr = document.createElement('tr');
        tr.className = "hover:bg-slate-800/40";
        tr.innerHTML = `
          <td class="p-2.5 font-mono text-slate-500">${r.row_number}</td>
          <td class="p-2.5 font-bold text-white">${r.term}</td>
          <td class="p-2.5 font-mono text-emerald-400 text-[11px]">${r.ipa || '<span class="text-slate-600">—</span>'}</td>
          <td class="p-2.5 text-slate-300 truncate max-w-xs">${r.definition}</td>
          <td class="p-2.5 text-teal-300">${r.part_of_speech || '—'}</td>
          <td class="p-2.5">${r.is_root_marker ? '<span class="text-indigo-400 font-bold">↳ Phát hiện từ gốc</span>' : '—'}</td>
        `;
        tbody.appendChild(tr);
      });
    }

    async function executeImportData() {
      const deckId = document.getElementById('importTargetDeck').value;
      const dedup = document.getElementById('importDedupMode').value;
      if (!deckId) return alert('Vui lòng chọn bộ thẻ');

      try {
        const isFile = !document.getElementById('importFileSection').classList.contains('hidden');
        let res;
        if (isFile) {
          if (!selectedWizardFile) return alert('Vui lòng chọn tệp');
          const formData = new FormData();
          formData.append('file', selectedWizardFile);
          res = await apiRequest(`/api/decks/${deckId}/import?dedup_strategy=${dedup}`, {
            method: 'POST',
            body: formData,
            isFormData: true
          });
        } else {
          const text = document.getElementById('wizardPasteInput').value.trim();
          if (!text) return alert('Vui lòng dán dữ liệu');
          res = await apiRequest(`/api/decks/${deckId}/import/paste`, {
            method: 'POST',
            body: JSON.stringify({ text_data: text, dedup_strategy: dedup })
          });
        }

        alert(`Nhập thành công: ${res.imported_count} từ mới! Bỏ qua: ${res.skipped_count || 0}.`);
        navigateTo('dashboard');
      } catch (err) {
        alert(err.message);
      }
    }

    // PROGRESS VIEW
    async function loadProgressView() {
      try {
        const [streak, stages] = await Promise.all([
          apiRequest(`/api/progress/streak?language=${currentLearningLanguage}`),
          apiRequest(`/api/progress/skills?language=${currentLearningLanguage}`)
        ]);

        document.getElementById('progCurrentStreak').textContent = `${streak.current_streak} ngày`;
        document.getElementById('progLongestStreak').textContent = `${streak.longest_streak} ngày`;
        document.getElementById('progActiveDays').textContent = `${streak.active_days_count} ngày`;

        // Render mock/real heatmap
        const heat = document.getElementById('activityHeatmap');
        heat.innerHTML = '';
        for (let i = 29; i >= 0; i--) {
          const d = document.createElement('div');
          const active = i < streak.current_streak;
          d.className = `w-7 h-7 rounded-lg flex items-center justify-center text-[9px] font-mono font-bold transition ${active ? 'bg-emerald-600 text-white shadow' : 'bg-slate-800 text-slate-500'}`;
          d.textContent = 30 - i;
          heat.appendChild(d);
        }

        document.getElementById('srsStageNew').textContent = stages.new_cards || 0;
        document.getElementById('srsStageLearning').textContent = stages.learning_cards || 0;
        document.getElementById('srsStageReview').textContent = stages.review_cards || 0;
        document.getElementById('srsStageLapsed').textContent = stages.lapsed_cards || 0;
      } catch (e) {
        console.error(e);
      }
    }

    // SETTINGS VIEW
    async function loadSettingsView() {
      if (!currentUser) await fetchUserProfile();
      document.getElementById('settingLearningLang').value = currentLearningLanguage;
      if (currentUser) {
        if (currentUser.english_voice_preference) {
          document.getElementById('settingEnglishVoice').value = currentUser.english_voice_preference;
        }
        if (currentUser.chinese_voice_preference) {
          document.getElementById('settingChineseVoice').value = currentUser.chinese_voice_preference;
        }
        if (currentUser.daily_new_target) {
          document.getElementById('settingDailyNewTarget').value = currentUser.daily_new_target;
        }
        if (currentUser.daily_review_target) {
          document.getElementById('settingDailyReviewTarget').value = currentUser.daily_review_target;
        }
        if (currentUser.daily_time_goal) {
          document.getElementById('settingDailyTimeGoal').value = currentUser.daily_time_goal;
        }
      }
      handleSettingLangChange(currentLearningLanguage);
    }

    function handleSettingLangChange(lang) {
      const grp = document.getElementById('settingScriptPrefGroup');
      if (lang === 'zh') grp.classList.remove('hidden');
      else grp.classList.add('hidden');
    }

    async function saveUserSettings() {
      const newLang = document.getElementById('settingLearningLang').value;
      const scriptPref = document.getElementById('settingScriptPref').value;
      const enVoice = document.getElementById('settingEnglishVoice').value;
      const zhVoice = document.getElementById('settingChineseVoice').value;
      const dailyNew = parseInt(document.getElementById('settingDailyNewTarget').value, 10);
      const dailyRev = parseInt(document.getElementById('settingDailyReviewTarget').value, 10);
      const dailyTime = parseInt(document.getElementById('settingDailyTimeGoal').value, 10);

      try {
        const updated = await apiRequest('/api/auth/settings', {
          method: 'PUT',
          body: JSON.stringify({
            active_learning_language: newLang,
            script_preference: scriptPref,
            english_voice_preference: enVoice,
            chinese_voice_preference: zhVoice,
            daily_new_target: dailyNew,
            daily_review_target: dailyRev,
            daily_time_goal: dailyTime
          })
        });
        currentUser = updated;
        currentLearningLanguage = newLang;
        document.getElementById('headerLangSelect').value = newLang;
        updateWorkspaceBadge();
        alert('Cài đặt đã được lưu thành công!');
        navigateTo('dashboard');
      } catch (err) {
        alert('Lỗi: ' + err.message);
      }
    }

    // Create Deck, Path & Manual Vocab Handlers
    function openCreateDeckModal() {
      document.getElementById('deckModalLang').value = currentLearningLanguage;
      openModal('modalCreateDeck');
    }
    function openCreatePathModal() { openModal('modalCreatePath'); }

    function openCreateVocabModal() {
      const sel = document.getElementById('manualVocabDeck');
      sel.innerHTML = '';
      const filteredDecks = allDecks.filter(d => !currentLearningLanguage || d.target_language === currentLearningLanguage);
      if (filteredDecks.length === 0) {
        const langName = currentLearningLanguage === 'zh' ? 'Tiếng Trung' : 'Tiếng Anh';
        alert(`Vui lòng tạo ít nhất 1 Bộ thẻ ${langName} trước khi thêm từ vựng!`);
        openCreateDeckModal();
        return;
      }
      filteredDecks.forEach(d => {
        sel.innerHTML += `<option value="${d.id}">${d.name} (${d.target_language.toUpperCase()})</option>`;
      });

      const isChinese = (currentLearningLanguage === 'zh');
      document.getElementById('manualVocabTermLabel').textContent = isChinese ? 'Hán Tự (Hanzi) *' : 'Từ Vựng (English Word) *';
      document.getElementById('manualVocabTerm').placeholder = isChinese ? 'e.g. 学习' : 'e.g. serendipity';
      document.getElementById('manualVocabIpaLabel').textContent = isChinese ? 'Phiên Âm (Pinyin có thanh điệu) *' : 'Phiên Âm (IPA)';
      document.getElementById('manualVocabIpa').placeholder = isChinese ? 'e.g. xué xí' : 'e.g. /ˌser.ənˈdɪp.ə.ti/';

      document.getElementById('vocabEnglishFields').classList.toggle('hidden', isChinese);
      document.getElementById('vocabChineseFields').classList.toggle('hidden', !isChinese);

      document.getElementById('manualVocabTerm').value = '';
      document.getElementById('manualVocabIpa').value = '';
      document.getElementById('manualVocabDef').value = '';
      document.getElementById('manualVocabExample').value = '';
      document.getElementById('manualVocabRoot').value = '';
      document.getElementById('manualVocabMnemonic').value = '';
      openModal('modalCreateVocab');
    }

    function previewManualTts() {
      const term = document.getElementById('manualVocabTerm').value.trim();
      if (term) speakText(term, currentLearningLanguage || 'en');
    }

    async function handleCreateVocabManual(e) {
      e.preventDefault();
      const deckId = document.getElementById('manualVocabDeck').value;
      const term = document.getElementById('manualVocabTerm').value.trim();
      const ipa = document.getElementById('manualVocabIpa').value.trim();
      const definition = document.getElementById('manualVocabDef').value.trim();
      const exampleText = document.getElementById('manualVocabExample').value.trim();
      const rootWord = document.getElementById('manualVocabRoot').value.trim();
      const mnemonic = document.getElementById('manualVocabMnemonic').value.trim();

      const examples = exampleText ? [exampleText] : [];
      const isChinese = (currentLearningLanguage === 'zh');

      let payload;
      if (isChinese) {
        const hsk = document.getElementById('manualVocabHsk').value;
        const trad = document.getElementById('manualVocabTrad').value.trim();
        payload = {
          deck_id: deckId,
          term: term,
          definition: definition,
          language: 'zh',
          ipa: '',
          part_of_speech: 'Hán tự',
          examples: examples,
          root_word: rootWord,
          mnemonics: mnemonic,
          vietnamese_meanings: [definition],
          language_specific_fields: {
            simplified: term,
            traditional: trad || term,
            pinyin: ipa,
            hsk_level: hsk
          }
        };
      } else {
        const pos = document.getElementById('manualVocabPos').value;
        payload = {
          deck_id: deckId,
          term: term,
          definition: definition,
          language: 'en',
          ipa: ipa,
          part_of_speech: pos,
          examples: examples,
          root_word: rootWord,
          mnemonics: mnemonic,
          vietnamese_meanings: [definition],
          language_specific_fields: {}
        };
      }

      try {
        await apiRequest('/api/vocab', {
          method: 'POST',
          body: JSON.stringify(payload)
        });

        closeModal('modalCreateVocab');
        alert(`Đã thêm từ vựng "${term}" vào bộ thẻ thành công! Thẻ SRS đã được tự động khởi tạo.`);
        if (currentView === 'vocab') {
          await loadVocabView();
        } else {
          await loadDashboard();
        }
      } catch (err) {
        alert('Lỗi: ' + err.message);
      }
    }

    async function handleCreateDeck(e) {
      e.preventDefault();
      const name = document.getElementById('deckModalName').value.trim();
      const target_language = document.getElementById('deckModalLang').value;
      const description = document.getElementById('deckModalDesc').value.trim();
      const tagsInput = document.getElementById('deckModalTags').value.trim();
      const tags = tagsInput ? tagsInput.split(',').map(s => s.trim()).filter(Boolean) : [];
      const max_new = parseInt(document.getElementById('deckModalMaxNew').value, 10) || 10;
      const max_rev = parseInt(document.getElementById('deckModalMaxRev').value, 10) || 50;

      try {
        await apiRequest('/api/decks', {
          method: 'POST',
          body: JSON.stringify({
            name,
            target_language,
            description,
            tags,
            max_new_cards_per_day: max_new,
            max_reviews_per_day: max_rev
          })
        });
        closeModal('modalCreateDeck');
        navigateTo('dashboard');
      } catch (err) {
        alert(err.message);
      }
    }

    async function handleCreatePath(e) {
      e.preventDefault();
      const name = document.getElementById('pathModalName').value.trim();
      const learning_language = document.getElementById('pathModalLang').value;
      const objective = document.getElementById('pathModalObjective').value.trim();
      const daily_new_target = parseInt(document.getElementById('pathModalDailyNew').value, 10);
      const daily_time_goal = parseInt(document.getElementById('pathModalDailyTime').value, 10);

      try {
        await apiRequest('/api/paths', {
          method: 'POST',
          body: JSON.stringify({ name, learning_language, objective, daily_new_target, daily_time_goal })
        });
        closeModal('modalCreatePath');
        navigateTo('paths');
      } catch (err) {
        alert(err.message);
      }
    }

    // Bootstrapping App
    window.addEventListener('DOMContentLoaded', async () => {
      if (authToken) {
        await fetchUserProfile();
        navigateTo('dashboard');
      } else {
        updateAuthHeaderUI();
        navigateTo('auth');
      }
    });
  </script>
</body>
</html>
"""

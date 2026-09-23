/**
 * KATCHO — Real-Time Multiplayer Social Deduction & Memory Game
 * Client Logic: WebSockets, Audio Synth, Visual Moderator, Truth Lock, 1 vs 2 Words Mode
 * Branding: Created by KABIR VYAS
 */

(() => {
  'use strict';

  // State
  let ws = null;
  let playerId = null;
  let roomCode = null;
  let isHost = false;
  let wordsPerPlayer = 1;
  let soundEnabled = true;
  let pingInterval = null;
  let localSecretWords = [];
  let isFlashRunning = false;

  const FLASH_COLORS = [
    '#FFEAA7', '#FF7675', '#55EFC4', '#74B9FF', '#A29BFE',
    '#FD79A8', '#FDCB6E', '#00CEC9', '#81ECEC', '#FAB1A0'
  ];

  // DOM Elements
  const els = {
    // Header
    roomBadge: document.getElementById('roomBadge'),
    roomCodeText: document.getElementById('roomCodeText'),
    connectionStatus: document.getElementById('connectionStatus'),
    statusText: document.getElementById('statusText'),
    btnLanModal: document.getElementById('btnLanModal'),
    btnSoundToggle: document.getElementById('btnSoundToggle'),
    btnRulesModal: document.getElementById('btnRulesModal'),
    btnLeaveRoom: document.getElementById('btnLeaveRoom'),
    toastContainer: document.getElementById('toastContainer'),

    // Views
    viewEntry: document.getElementById('viewEntry'),
    viewGame: document.getElementById('viewGame'),

    // Entry Form
    inputPlayerName: document.getElementById('inputPlayerName'),
    btnCreateRoom: document.getElementById('btnCreateRoom'),
    inputRoomCode: document.getElementById('inputRoomCode'),
    btnJoinRoom: document.getElementById('btnJoinRoom'),
    linkOpenLanFromEntry: document.getElementById('linkOpenLanFromEntry'),

    // Stage Subviews
    stagePhaseLobby: document.getElementById('stagePhaseLobby'),
    stagePhaseReveal: document.getElementById('stagePhaseReveal'),
    stagePhaseGuessing: document.getElementById('stagePhaseGuessing'),
    stagePhaseGameOver: document.getElementById('stagePhaseGameOver'),

    // Phase 1: Lobby
    currentModeLabel: document.getElementById('currentModeLabel'),
    btnHostChangeMode: document.getElementById('btnHostChangeMode'),
    readyCountBadge: document.getElementById('readyCountBadge'),
    wordInstructionText: document.getElementById('wordInstructionText'),
    wordHintText: document.getElementById('wordHintText'),
    
    // Single Word
    singleWordInputWrap: document.getElementById('singleWordInputWrap'),
    inputSecretWord1: document.getElementById('inputSecretWord1'),
    btnSubmitSingleWord: document.getElementById('btnSubmitSingleWord'),
    
    // Double Word
    doubleWordInputWrap: document.getElementById('doubleWordInputWrap'),
    inputDoubleWord1: document.getElementById('inputDoubleWord1'),
    inputDoubleWord2: document.getElementById('inputDoubleWord2'),
    btnSubmitDoubleWord: document.getElementById('btnSubmitDoubleWord'),

    wordInputUnlocked: document.getElementById('wordInputUnlocked'),
    wordInputLocked: document.getElementById('wordInputLocked'),
    lockedCountLabel: document.getElementById('lockedCountLabel'),
    myLockedWordsList: document.getElementById('myLockedWordsList'),
    btnEditWord: document.getElementById('btnEditWord'),

    hostLobbyControls: document.getElementById('hostLobbyControls'),
    btnStartReveal: document.getElementById('btnStartReveal'),
    hostStartHelper: document.getElementById('hostStartHelper'),

    // Phase 2: Reveal Flash
    flashProgressText: document.getElementById('flashProgressText'),
    flashWordDisplay: document.getElementById('flashWordDisplay'),
    flashProgressBar: document.getElementById('flashProgressBar'),

    // Phase 3: Guessing
    activeTurnPlayerText: document.getElementById('activeTurnPlayerText'),
    announcementBillboard: document.getElementById('announcementBillboard'),
    announcementIcon: document.getElementById('announcementIcon'),
    announcementMain: document.getElementById('announcementMain'),
    announcementSub: document.getElementById('announcementSub'),

    // Phase 4: Game Over
    winnerTitle: document.getElementById('winnerTitle'),
    winnerSubtitle: document.getElementById('winnerSubtitle'),
    revealTableBody: document.getElementById('revealTableBody'),
    btnPlayAgain: document.getElementById('btnPlayAgain'),

    // Roster
    rosterCount: document.getElementById('rosterCount'),
    playerRosterGrid: document.getElementById('playerRosterGrid'),

    // Turn Actions
    turnActionContainer: document.getElementById('turnActionContainer'),
    selectTargetPlayer: document.getElementById('selectTargetPlayer'),
    inputAccusedWord: document.getElementById('inputAccusedWord'),
    btnAccuse: document.getElementById('btnAccuse'),
    btnPassTurn: document.getElementById('btnPassTurn'),
    btnCallDraw: document.getElementById('btnCallDraw'),

    // Scratchpad
    privateScratchpad: document.getElementById('privateScratchpad'),
    btnClearScratchpad: document.getElementById('btnClearScratchpad'),

    // Modals
    modalWordMode: document.getElementById('modalWordMode'),
    btnChooseMode1: document.getElementById('btnChooseMode1'),
    btnChooseMode2: document.getElementById('btnChooseMode2'),
    btnCloseModeModal: document.getElementById('btnCloseModeModal'),

    modalTruthLock: document.getElementById('modalTruthLock'),
    modalGuesserName: document.getElementById('modalGuesserName'),
    modalAccusedWord: document.getElementById('modalAccusedWord'),
    truthButtonsContainer: document.getElementById('truthButtonsContainer'),

    modalDrawVote: document.getElementById('modalDrawVote'),
    drawVotePrompt: document.getElementById('drawVotePrompt'),
    drawVoteTally: document.getElementById('drawVoteTally'),
    btnVoteAgree: document.getElementById('btnVoteAgree'),
    btnVoteDisagree: document.getElementById('btnVoteDisagree'),

    modalLanInfo: document.getElementById('modalLanInfo'),
    qrCodeImage: document.getElementById('qrCodeImage'),
    inputLanUrl: document.getElementById('inputLanUrl'),
    btnCopyLanUrl: document.getElementById('btnCopyLanUrl'),
    btnCloseLanModal: document.getElementById('btnCloseLanModal'),

    // Install / Download PWA Modal Elements
    btnHeaderInstallApp: document.getElementById('btnHeaderInstallApp'),
    cardChoicePlayOnline: document.getElementById('cardChoicePlayOnline'),
    cardChoiceDownloadApp: document.getElementById('cardChoiceDownloadApp'),
    btnQuickInstall: document.getElementById('btnQuickInstall'),
    modalInstallApp: document.getElementById('modalInstallApp'),
    btnInstallNativePrompt: document.getElementById('btnInstallNativePrompt'),
    btnCloseInstallModal: document.getElementById('btnCloseInstallModal'),

    modalRules: document.getElementById('modalRules'),
    btnCloseRulesModal: document.getElementById('btnCloseRulesModal'),
  };

  // ===================================================================
  // AUDIO SYNTHESIZER
  // ===================================================================
  const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

  function playTone(freq, duration, type = 'sine', gainVal = 0.15) {
    if (!soundEnabled) return;
    try {
      if (audioCtx.state === 'suspended') audioCtx.resume();
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
      gain.gain.setValueAtTime(gainVal, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + duration);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(audioCtx.currentTime + duration);
    } catch (e) {
      console.warn('Audio play error:', e);
    }
  }

  const sounds = {
    click: () => playTone(600, 0.05, 'triangle', 0.1),
    tick: () => playTone(880, 0.08, 'sine', 0.12),
    success: () => {
      playTone(523.25, 0.15, 'sine', 0.15);
      setTimeout(() => playTone(659.25, 0.15, 'sine', 0.15), 100);
      setTimeout(() => playTone(783.99, 0.3, 'sine', 0.2), 200);
    },
    error: () => {
      playTone(220, 0.25, 'sawtooth', 0.15);
      setTimeout(() => playTone(180, 0.3, 'sawtooth', 0.15), 120);
    },
    fanfare: () => {
      [523.25, 659.25, 783.99, 1046.50].forEach((freq, i) => {
        setTimeout(() => playTone(freq, 0.35, 'triangle', 0.2), i * 150);
      });
    }
  };

  // ===================================================================
  // INITIALIZATION
  // ===================================================================
  function init() {
    playerId = localStorage.getItem('katcho_player_id');
    if (!playerId) {
      playerId = 'p_' + Math.random().toString(36).substr(2, 9);
      localStorage.setItem('katcho_player_id', playerId);
    }

    const savedName = localStorage.getItem('katcho_player_name');
    if (savedName && els.inputPlayerName) {
      els.inputPlayerName.value = savedName;
    }

    const savedSound = localStorage.getItem('katcho_sound_enabled');
    if (savedSound !== null) {
      soundEnabled = savedSound === 'true';
      updateSoundIcon();
    }

    const urlParams = new URLSearchParams(window.location.search);
    const paramRoom = urlParams.get('room');
    if (paramRoom && els.inputRoomCode) {
      els.inputRoomCode.value = paramRoom.toUpperCase();
    }

    loadScratchpad();
    bindEvents();
    fetchLanInfo();
  }

  function updateSoundIcon() {
    els.btnSoundToggle.textContent = soundEnabled ? '🔊' : '🔇';
  }

  function loadScratchpad() {
    const key = roomCode ? `katcho_scratch_${roomCode}` : 'katcho_scratch_default';
    els.privateScratchpad.value = localStorage.getItem(key) || '';
  }

  function saveScratchpad() {
    const key = roomCode ? `katcho_scratch_${roomCode}` : 'katcho_scratch_default';
    localStorage.setItem(key, els.privateScratchpad.value);
  }

  function showToast(msg, type = 'info') {
    const toast = document.createElement('div');
    toast.className = 'toast-msg';
    if (type === 'error') toast.style.background = '#FF4757';
    if (type === 'success') toast.style.background = '#2ED573';
    toast.textContent = msg;
    els.toastContainer.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transition = 'opacity 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  }

  // ===================================================================
  // WEBSOCKETS
  // ===================================================================
  function connectWebSocket(targetRoom) {
    if (ws) {
      try { ws.close(); } catch(e) {}
    }

    setConnectionStatus('connecting', 'Connecting...');
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/ws/${targetRoom}/${playerId}`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      setConnectionStatus('online', 'Online');
      startPing();
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        handleServerMessage(data);
      } catch (e) {
        console.error('JSON parse error:', e);
      }
    };

    ws.onerror = (err) => {
      console.warn('WebSocket error:', err);
      setConnectionStatus('offline', 'Error');
    };

    ws.onclose = () => {
      setConnectionStatus('offline', 'Disconnected');
      stopPing();
    };
  }

  function sendAction(action, payload = {}) {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      showToast('Not connected to server', 'error');
      return;
    }
    const msg = Object.assign({ action }, payload);
    ws.send(JSON.stringify(msg));
  }

  function startPing() {
    stopPing();
    pingInterval = setInterval(() => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ action: 'ping' }));
      }
    }, 15000);
  }

  function stopPing() {
    if (pingInterval) {
      clearInterval(pingInterval);
      pingInterval = null;
    }
  }

  function setConnectionStatus(status, text) {
    els.connectionStatus.className = `status-indicator ${status}`;
    els.statusText.textContent = text;
  }

  // ===================================================================
  // MESSAGE HANDLER
  // ===================================================================
  function handleServerMessage(data) {
    if (data.type === 'error') {
      showToast(data.message, 'error');
      sounds.error();
      return;
    }

    if (data.type === 'prompt_mode_selection') {
      if (isHost) {
        els.modalWordMode.classList.remove('hidden');
      }
      return;
    }

    if (data.type === 'state_update') {
      renderGameState(data.state);
    }

    if (data.event) {
      handleCustomEvent(data.event);
    }
  }

  function handleCustomEvent(ev) {
    if (ev.type === 'room_created') {
      roomCode = ev.room_code;
      showToast(`Room ${roomCode} created!`, 'success');
      sounds.success();
    } else if (ev.type === 'reveal_started') {
      startVisualModeratorSequence(ev.word_sequence);
    } else if (ev.type === 'accusation_resolved') {
      if (ev.result.is_correct) {
        sounds.success();
      } else {
        sounds.error();
      }
    } else if (ev.type === 'word_mode_changed') {
      showToast(`Match set to ${ev.words_per_player} word(s) per player!`, 'info');
      sounds.tick();
    } else if (ev.type === 'game_reset') {
      localSecretWords = [];
      els.inputSecretWord1.value = '';
      els.inputDoubleWord1.value = '';
      els.inputDoubleWord2.value = '';
      els.wordInputLocked.classList.add('hidden');
      els.wordInputUnlocked.classList.remove('hidden');
      showToast('New round started! Submit your secret words.', 'info');
    }
  }

  // ===================================================================
  // STATE RENDERING
  // ===================================================================
  function renderGameState(state) {
    if (!state) return;

    roomCode = state.room_code;
    isHost = state.is_host;
    wordsPerPlayer = state.words_per_player || 1;

    els.roomCodeText.textContent = roomCode;
    els.roomBadge.classList.remove('hidden');
    els.btnLeaveRoom.classList.remove('hidden');

    els.viewEntry.classList.remove('active');
    els.viewEntry.classList.add('hidden');
    els.viewGame.classList.remove('hidden');
    els.viewGame.classList.add('active');

    renderStagePhase(state);
    renderRoster(state);
    renderTurnControls(state);
    renderTruthLockModal(state);
    renderDrawVoteModal(state);
  }

  function renderStagePhase(state) {
    els.stagePhaseLobby.classList.add('hidden');
    els.stagePhaseReveal.classList.add('hidden');
    els.stagePhaseGuessing.classList.add('hidden');
    els.stagePhaseGameOver.classList.add('hidden');

    if (state.phase === 'LOBBY') {
      els.stagePhaseLobby.classList.remove('hidden');
      
      // Mode Label
      const modeText = state.words_per_player === 2 
        ? 'Mode: 2 Words (Double Word)' 
        : 'Mode: 1 Word per Player';
      els.currentModeLabel.textContent = modeText;

      if (isHost && state.total_players < 7) {
        els.btnHostChangeMode.classList.remove('hidden');
      } else {
        els.btnHostChangeMode.classList.add('hidden');
      }

      els.readyCountBadge.textContent = `${state.submitted_count} / ${state.total_players} Ready`;

      // Word Input Forms based on mode
      if (state.words_per_player === 2) {
        els.singleWordInputWrap.classList.add('hidden');
        els.doubleWordInputWrap.classList.remove('hidden');
        els.wordInstructionText.innerHTML = '🔒 <strong>Step 1:</strong> Enter <strong>two</strong> secret words one after the other. Keep them secret!';
        els.wordHintText.textContent = 'Enter two distinct words. Example: GALAXY and MANGO';
      } else {
        els.singleWordInputWrap.classList.remove('hidden');
        els.doubleWordInputWrap.classList.add('hidden');
        els.wordInstructionText.innerHTML = '🔒 <strong>Step 1:</strong> Enter your secret word. Keep it secret from everyone!';
        els.wordHintText.textContent = 'Uppercase, trimmed automatically. Example: GALAXY, MANGO, PIRATE';
      }

      // Check if self has submitted required words
      const me = state.players.find(p => p.id === playerId);
      if (me && me.has_submitted_word) {
        els.wordInputUnlocked.classList.add('hidden');
        els.wordInputLocked.classList.remove('hidden');
        
        const myWords = me.secret_words || localSecretWords || ['LOCKED'];
        els.lockedCountLabel.textContent = `Your ${myWords.length} Secret Word${myWords.length > 1 ? 's are' : ' is'} Locked:`;
        
        els.myLockedWordsList.innerHTML = '';
        myWords.forEach((w, idx) => {
          const chip = document.createElement('span');
          chip.className = 'locked-word-chip';
          chip.textContent = `#${idx + 1}: ${w}`;
          els.myLockedWordsList.appendChild(chip);
        });
      } else {
        els.wordInputUnlocked.classList.remove('hidden');
        els.wordInputLocked.classList.add('hidden');
      }

      // Host controls
      if (isHost) {
        els.hostLobbyControls.classList.remove('hidden');
        const canStart = state.total_players >= 2 && state.submitted_count === state.total_players;
        els.btnStartReveal.disabled = !canStart;
        els.hostStartHelper.textContent = canStart 
          ? '🎉 All players ready! Click to begin the reveal sequence.'
          : `Waiting for all players to submit words (${state.submitted_count}/${state.total_players}, min 2 players)...`;
      } else {
        els.hostLobbyControls.classList.add('hidden');
      }

    } else if (state.phase === 'REVEAL') {
      els.stagePhaseReveal.classList.remove('hidden');

    } else if (state.phase === 'GUESSING') {
      els.stagePhaseGuessing.classList.remove('hidden');
      
      const turnName = state.current_turn_player_name || 'Someone';
      els.activeTurnPlayerText.textContent = state.is_my_turn ? 'YOUR TURN' : `${turnName}'s Turn`;

      if (state.recent_announcement) {
        const ann = state.recent_announcement;
        els.announcementMain.textContent = ann.text;
        els.announcementBillboard.className = `announcement-board ${ann.category || 'info'}`;
        
        if (ann.category === 'success') {
          els.announcementIcon.textContent = '💥';
          els.announcementSub.textContent = 'Bingo! Correct accusation!';
        } else if (ann.category === 'error') {
          els.announcementIcon.textContent = '❌';
          els.announcementSub.textContent = 'Wrong guess! Turn transferred to the accused.';
        } else if (ann.category === 'warning') {
          els.announcementIcon.textContent = '⚡';
          els.announcementSub.textContent = 'Accusation in progress...';
        } else {
          els.announcementIcon.textContent = '🎯';
          els.announcementSub.textContent = `${turnName} is deciding the next move.`;
        }
      }

    } else if (state.phase === 'GAME_OVER') {
      els.stagePhaseGameOver.classList.remove('hidden');
      sounds.fanfare();

      if (state.is_draw) {
        els.winnerTitle.textContent = 'MATCH ENDED IN A DRAW! 🤝';
        els.winnerSubtitle.textContent = 'All players unanimously agreed to a draw.';
      } else {
        els.winnerTitle.textContent = `🏆 ${state.winner_name || 'WINNER'} WINS!`;
        els.winnerSubtitle.textContent = 'The last uncaught player standing!';
      }

      renderRevealTable(state.players, state.winner_id, state.is_draw);
    }
  }

  function renderRevealTable(players, winnerId, isDraw) {
    els.revealTableBody.innerHTML = '';
    
    players.forEach(p => {
      const row = document.createElement('tr');
      const isWinner = !isDraw && (p.id === winnerId);
      
      let statusTag = '';
      if (isWinner) {
        statusTag = '<span class="status-tag status-winner">👑 Winner</span>';
      } else if (p.is_caught) {
        statusTag = '<span class="status-tag status-caught">🎯 Caught</span>';
      } else if (isDraw) {
        statusTag = '<span class="status-tag status-draw">🤝 Draw</span>';
      } else {
        statusTag = '<span class="status-tag status-winner">✨ Survivor</span>';
      }

      let elimText = '—';
      if (isWinner) {
        elimText = '<strong>— (Winner)</strong>';
      } else if (p.eliminated_by) {
        elimText = `Eliminated by <strong>${p.eliminated_by}</strong>`;
      } else if (p.is_caught) {
        elimText = 'Eliminated';
      }

      // Display words chips
      const wordsArray = p.secret_words || [];
      const wordsDisplay = wordsArray.length > 0 
        ? wordsArray.map(w => `<span class="word-cell">${escapeHtml(w)}</span>`).join(', ')
        : 'UNKNOWN';

      row.innerHTML = `
        <td class="player-cell">
          <span class="player-avatar" style="background-color: ${p.color}; width: 24px; height: 24px; font-size: 0.75rem;">
            ${p.name.charAt(0).toUpperCase()}
          </span>
          <span>${escapeHtml(p.name)} ${p.is_host ? '👑' : ''}</span>
        </td>
        <td>${wordsDisplay}</td>
        <td>${statusTag}</td>
        <td><strong>${p.correct_guesses || 0}</strong></td>
        <td>${elimText}</td>
      `;
      els.revealTableBody.appendChild(row);
    });
  }

  function renderRoster(state) {
    els.rosterCount.textContent = state.players.length;
    els.playerRosterGrid.innerHTML = '';

    state.players.forEach(p => {
      const isTurn = (state.phase === 'GUESSING' && p.id === state.current_turn_player_id);
      const isMe = (p.id === playerId);
      
      const card = document.createElement('div');
      card.className = `player-card ${isTurn ? 'active-turn' : ''} ${p.is_caught ? 'is-caught' : ''}`;

      let statusBadge = '';
      if (state.phase === 'LOBBY') {
        const req = state.words_per_player || 1;
        const sub = p.submitted_words_count || 0;
        statusBadge = p.has_submitted_word 
          ? '<span class="badge-ready">✓ Ready</span>' 
          : `<span class="badge-waiting">⋯ ${sub}/${req} Words</span>`;
      } else {
        if (p.is_caught) {
          statusBadge = '<span class="badge-caught">💥 Caught</span>';
        } else {
          statusBadge = '<span class="badge-alive">🛡️ Alive</span>';
        }
      }

      card.innerHTML = `
        <div class="player-card-header">
          <div class="player-avatar" style="background-color: ${p.color};">
            ${p.name.charAt(0).toUpperCase()}
          </div>
          <div class="player-name-wrap">
            <span class="player-name">${escapeHtml(p.name)} ${isMe ? '(You)' : ''}</span>
            ${p.is_host ? '<span class="player-host-tag" title="Host">👑</span>' : ''}
          </div>
        </div>
        <div class="player-card-status">
          ${statusBadge}
          <span class="player-score-tag" title="Correct Deductions">🎯 ${p.correct_guesses || 0}</span>
        </div>
      `;
      els.playerRosterGrid.appendChild(card);
    });
  }

  function renderTurnControls(state) {
    if (state.phase === 'GUESSING' && state.is_my_turn) {
      els.turnActionContainer.classList.remove('hidden');

      const currentTarget = els.selectTargetPlayer.value;
      els.selectTargetPlayer.innerHTML = '<option value="">-- Choose Target Player --</option>';

      state.players.forEach(p => {
        if (p.id !== playerId) {
          const opt = document.createElement('option');
          opt.value = p.id;
          opt.textContent = `${p.name} ${p.is_caught ? '(Caught)' : '(Alive)'}`;
          if (p.id === currentTarget) opt.selected = true;
          els.selectTargetPlayer.appendChild(opt);
        }
      });
    } else {
      els.turnActionContainer.classList.add('hidden');
    }
  }

  function renderTruthLockModal(state) {
    const acc = state.active_accusation;
    if (acc && !acc.resolved && acc.target_id === playerId) {
      els.modalGuesserName.textContent = acc.guesser_name;
      els.modalAccusedWord.textContent = `"${acc.guessed_word}"`;
      els.truthButtonsContainer.innerHTML = '';

      const isTruth = acc.truth_answer;
      const btn = document.createElement('button');
      
      if (isTruth) {
        btn.className = 'btn btn-truth-yes pulse-glow';
        btn.innerHTML = '✅ YES! (That is my word)';
        btn.onclick = () => {
          sounds.click();
          sendAction('respond_accusation', { response: true });
          els.modalTruthLock.classList.add('hidden');
        };
      } else {
        btn.className = 'btn btn-truth-no pulse-glow';
        btn.innerHTML = '❌ NO! (Not my word)';
        btn.onclick = () => {
          sounds.click();
          sendAction('respond_accusation', { response: false });
          els.modalTruthLock.classList.add('hidden');
        };
      }

      els.truthButtonsContainer.appendChild(btn);
      els.modalTruthLock.classList.remove('hidden');
    } else {
      els.modalTruthLock.classList.add('hidden');
    }
  }

  function renderDrawVoteModal(state) {
    const draw = state.active_draw_vote;
    if (draw && state.phase === 'GUESSING') {
      els.drawVotePrompt.textContent = `${draw.initiator_name} called for a unanimous DRAW!`;
      els.drawVoteTally.textContent = `Votes: ${draw.votes_count} / ${draw.total_needed} Agreed`;
      els.modalDrawVote.classList.remove('hidden');
    } else {
      els.modalDrawVote.classList.add('hidden');
    }
  }

  // ===================================================================
  // VISUAL MODERATOR (WORD FLASH SEQUENCE)
  // ===================================================================
  function startVisualModeratorSequence(words) {
    if (!words || words.length === 0 || isFlashRunning) return;
    isFlashRunning = true;

    els.stagePhaseLobby.classList.add('hidden');
    els.stagePhaseReveal.classList.remove('hidden');

    const totalWords = words.length;
    let currentLoop = 1;
    let wordIndex = 0;

    function flashNext() {
      if (currentLoop > 2) {
        isFlashRunning = false;
        els.flashWordDisplay.textContent = 'GET READY TO DEDUCE!';
        els.flashWordDisplay.style.color = '#2ED573';
        els.flashProgressText.textContent = 'Sequence Complete!';
        
        if (isHost) {
          setTimeout(() => {
            sendAction('finish_reveal');
          }, 1200);
        }
        return;
      }

      const word = words[wordIndex];
      const color = FLASH_COLORS[(wordIndex + (currentLoop - 1) * 3) % FLASH_COLORS.length];

      els.flashWordDisplay.textContent = word;
      els.flashWordDisplay.style.color = color;
      els.flashWordDisplay.classList.remove('pop');
      void els.flashWordDisplay.offsetWidth;
      els.flashWordDisplay.classList.add('pop');

      els.flashProgressText.textContent = `Loop ${currentLoop}/2 • Word ${wordIndex + 1}/${totalWords}`;
      
      const totalSteps = totalWords * 2;
      const currentStep = (currentLoop - 1) * totalWords + (wordIndex + 1);
      const pct = (currentStep / totalSteps) * 100;
      els.flashProgressBar.style.width = `${pct}%`;

      sounds.tick();

      wordIndex++;
      if (wordIndex >= totalWords) {
        wordIndex = 0;
        currentLoop++;
      }

      setTimeout(flashNext, 3000);
    }

    els.flashWordDisplay.textContent = '3... 2... 1...';
    els.flashProgressBar.style.width = '0%';
    setTimeout(flashNext, 1200);
  }

  // ===================================================================
  // LAN & HOTSPOT
  // ===================================================================
  async function fetchLanInfo() {
    try {
      const res = await fetch('/api/lan-info');
      const data = await res.json();
      if (data && data.qr_data_url) {
        els.qrCodeImage.src = data.qr_data_url;
        els.inputLanUrl.value = data.lan_url;
      }
    } catch (e) {
      console.warn('LAN info fetch failed:', e);
    }
  }

  // ===================================================================
  // EVENT BINDINGS
  // ===================================================================
  function bindEvents() {
    els.inputPlayerName.addEventListener('input', () => {
      localStorage.setItem('katcho_player_name', els.inputPlayerName.value.trim());
    });

    els.btnCreateRoom.addEventListener('click', () => {
      sounds.click();
      const name = els.inputPlayerName.value.trim() || 'Host';
      localStorage.setItem('katcho_player_name', name);
      
      const tempCode = 'CREATE_' + Math.random().toString(36).substr(2, 4).toUpperCase();
      connectWebSocket(tempCode);

      const checkOpen = setInterval(() => {
        if (ws && ws.readyState === WebSocket.OPEN) {
          clearInterval(checkOpen);
          sendAction('create_room', { name });
        }
      }, 50);
    });

    els.btnJoinRoom.addEventListener('click', () => {
      sounds.click();
      const name = els.inputPlayerName.value.trim() || 'Player';
      const code = els.inputRoomCode.value.trim().toUpperCase();
      if (!code) {
        showToast('Please enter a 4-letter Room Code', 'error');
        return;
      }
      localStorage.setItem('katcho_player_name', name);
      connectWebSocket(code);

      const checkOpen = setInterval(() => {
        if (ws && ws.readyState === WebSocket.OPEN) {
          clearInterval(checkOpen);
          sendAction('join_room', { room_code: code, name });
        }
      }, 50);
    });

    // Word Mode Modal Buttons
    els.btnHostChangeMode.addEventListener('click', () => {
      sounds.click();
      els.modalWordMode.classList.remove('hidden');
    });

    els.btnChooseMode1.addEventListener('click', () => {
      sounds.click();
      sendAction('set_word_mode', { words_per_player: 1 });
      els.modalWordMode.classList.add('hidden');
    });

    els.btnChooseMode2.addEventListener('click', () => {
      sounds.click();
      sendAction('set_word_mode', { words_per_player: 2 });
      els.modalWordMode.classList.add('hidden');
    });

    els.btnCloseModeModal.addEventListener('click', () => {
      els.modalWordMode.classList.add('hidden');
    });

    // Single Word Submit
    els.inputSecretWord1.addEventListener('input', () => {
      els.inputSecretWord1.value = els.inputSecretWord1.value.toUpperCase();
    });

    els.btnSubmitSingleWord.addEventListener('click', () => {
      sounds.click();
      const word = els.inputSecretWord1.value.trim().toUpperCase();
      if (word.length < 2) {
        showToast('Secret word must be at least 2 letters', 'error');
        return;
      }
      localSecretWords = [word];
      sendAction('submit_word', { words: [word] });
    });

    // Double Word Submit
    els.inputDoubleWord1.addEventListener('input', () => {
      els.inputDoubleWord1.value = els.inputDoubleWord1.value.toUpperCase();
    });
    els.inputDoubleWord2.addEventListener('input', () => {
      els.inputDoubleWord2.value = els.inputDoubleWord2.value.toUpperCase();
    });

    els.btnSubmitDoubleWord.addEventListener('click', () => {
      sounds.click();
      const w1 = els.inputDoubleWord1.value.trim().toUpperCase();
      const w2 = els.inputDoubleWord2.value.trim().toUpperCase();
      if (w1.length < 2 || w2.length < 2) {
        showToast('Both secret words must be at least 2 letters', 'error');
        return;
      }
      if (w1 === w2) {
        showToast('Please enter two distinct secret words', 'error');
        return;
      }
      localSecretWords = [w1, w2];
      sendAction('submit_word', { words: [w1, w2] });
    });

    els.btnEditWord.addEventListener('click', () => {
      sounds.click();
      els.wordInputLocked.classList.add('hidden');
      els.wordInputUnlocked.classList.remove('hidden');
      if (wordsPerPlayer === 2) {
        els.inputDoubleWord1.focus();
      } else {
        els.inputSecretWord1.focus();
      }
    });

    // Host Start Reveal
    els.btnStartReveal.addEventListener('click', () => {
      sounds.click();
      sendAction('start_reveal');
    });

    // Accuse Action
    els.inputAccusedWord.addEventListener('input', () => {
      els.inputAccusedWord.value = els.inputAccusedWord.value.toUpperCase();
    });

    els.btnAccuse.addEventListener('click', () => {
      sounds.click();
      const targetId = els.selectTargetPlayer.value;
      const word = els.inputAccusedWord.value.trim().toUpperCase();
      if (!targetId) {
        showToast('Please select a Target Player', 'error');
        return;
      }
      if (!word) {
        showToast('Please enter the suspected word', 'error');
        return;
      }
      sendAction('make_accusation', { target_id: targetId, guessed_word: word });
      els.inputAccusedWord.value = '';
    });

    // Pass Turn
    els.btnPassTurn.addEventListener('click', () => {
      sounds.click();
      sendAction('pass_turn');
    });

    // Call Draw
    els.btnCallDraw.addEventListener('click', () => {
      sounds.click();
      if (confirm('Are you sure you want to call a vote for a DRAW?')) {
        sendAction('call_draw');
      }
    });

    els.btnVoteAgree.addEventListener('click', () => {
      sounds.click();
      sendAction('vote_draw', { agree: true });
      els.modalDrawVote.classList.add('hidden');
    });

    els.btnVoteDisagree.addEventListener('click', () => {
      sounds.click();
      sendAction('vote_draw', { agree: false });
      els.modalDrawVote.classList.add('hidden');
    });

    // Play Again
    els.btnPlayAgain.addEventListener('click', () => {
      sounds.click();
      sendAction('play_again');
    });

    // Scratchpad
    els.privateScratchpad.addEventListener('input', saveScratchpad);
    els.btnClearScratchpad.addEventListener('click', () => {
      if (confirm('Clear your private scratchpad?')) {
        els.privateScratchpad.value = '';
        saveScratchpad();
      }
    });

    // Modals
    els.roomBadge.addEventListener('click', () => {
      sounds.click();
      const link = `${window.location.origin}/?room=${roomCode}`;
      navigator.clipboard.writeText(link).then(() => {
        showToast('📋 Room invite link copied to clipboard!', 'success');
      }).catch(() => {
        showToast(`Room Code: ${roomCode}`, 'info');
      });
    });

    els.btnSoundToggle.addEventListener('click', () => {
      soundEnabled = !soundEnabled;
      localStorage.setItem('katcho_sound_enabled', soundEnabled);
      updateSoundIcon();
      if (soundEnabled) sounds.click();
    });

    els.btnLanModal.addEventListener('click', () => {
      sounds.click();
      fetchLanInfo();
      els.modalLanInfo.classList.remove('hidden');
    });

    els.linkOpenLanFromEntry.addEventListener('click', (e) => {
      e.preventDefault();
      sounds.click();
      fetchLanInfo();
      els.modalLanInfo.classList.remove('hidden');
    });

    els.btnCloseLanModal.addEventListener('click', () => {
      els.modalLanInfo.classList.add('hidden');
    });

    els.btnCopyLanUrl.addEventListener('click', () => {
      sounds.click();
      navigator.clipboard.writeText(els.inputLanUrl.value).then(() => {
        showToast('Hotspot URL copied!', 'success');
      });
    });

    els.btnRulesModal.addEventListener('click', () => {
      sounds.click();
      els.modalRules.classList.remove('hidden');
    });

    els.btnCloseRulesModal.addEventListener('click', () => {
      els.modalRules.classList.add('hidden');
    });

    els.btnLeaveRoom.addEventListener('click', () => {
      if (confirm('Leave this room and return to lobby?')) {
        window.location.href = '/';
      }
    });

    // PWA & Download App Handlers
    let deferredPrompt = null;
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      deferredPrompt = e;
      if (els.btnHeaderInstallApp) els.btnHeaderInstallApp.classList.remove('hidden');
    });

    function openInstallModal() {
      sounds.click();
      els.modalInstallApp.classList.remove('hidden');
    }

    if (els.btnHeaderInstallApp) {
      els.btnHeaderInstallApp.addEventListener('click', openInstallModal);
    }
    if (els.cardChoiceDownloadApp) {
      els.cardChoiceDownloadApp.addEventListener('click', openInstallModal);
    }
    if (els.btnQuickInstall) {
      els.btnQuickInstall.addEventListener('click', (e) => {
        e.stopPropagation();
        openInstallModal();
      });
    }

    if (els.cardChoicePlayOnline) {
      els.cardChoicePlayOnline.addEventListener('click', () => {
        sounds.click();
        els.cardChoicePlayOnline.classList.add('active');
        els.inputPlayerName.focus();
      });
    }

    if (els.btnInstallNativePrompt) {
      els.btnInstallNativePrompt.addEventListener('click', async () => {
        sounds.click();
        if (deferredPrompt) {
          deferredPrompt.prompt();
          const { outcome } = await deferredPrompt.userChoice;
          if (outcome === 'accepted') {
            showToast('🎉 KATCHO installed to your device!', 'success');
            els.modalInstallApp.classList.add('hidden');
          }
          deferredPrompt = null;
        } else {
          showToast('Use the guide below for your platform (Android, iOS, or PC)', 'info');
        }
      });
    }

    if (els.btnCloseInstallModal) {
      els.btnCloseInstallModal.addEventListener('click', () => {
        els.modalInstallApp.classList.add('hidden');
      });
    }

    // Register Service Worker for PWA
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register('/service-worker.js')
          .then((reg) => console.log('ServiceWorker registered:', reg.scope))
          .catch((err) => console.warn('ServiceWorker registration error:', err));
      });
    }

    window.addEventListener('click', (e) => {
      if (e.target === els.modalLanInfo) els.modalLanInfo.classList.add('hidden');
      if (e.target === els.modalRules) els.modalRules.classList.add('hidden');
      if (e.target === els.modalWordMode) els.modalWordMode.classList.add('hidden');
      if (e.target === els.modalInstallApp) els.modalInstallApp.classList.add('hidden');
    });
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/[&<>"']/g, (m) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    })[m]);
  }

  document.addEventListener('DOMContentLoaded', init);

})();

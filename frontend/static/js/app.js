const weightOptions = Array.from({ length: 91 }, (_, index) => index + 10);
const ageGroupSelect = document.querySelector('#age_group');
const currentWeightSelect = document.querySelector('#current_weight');
const desiredWeightSelect = document.querySelector('#desired_weight');
const form = document.querySelector('#profile-form');
const loadingSection = document.querySelector('#loading');
const resultsSection = document.querySelector('#results');
const loadingMessage = document.querySelector('#loading-message');
const progressBar = document.querySelector('#progress-bar');
const formMessage = document.querySelector('#form-message');
const submitButton = document.querySelector('#profile-form button[type="submit"]');
const authForm = document.querySelector('#auth-form');
const authMessage = document.querySelector('#auth-message');
const authUsernameInput = document.querySelector('#auth-username');
const authEmailInput = document.querySelector('#auth-email');
const authPasswordInput = document.querySelector('#auth-password');
const modeButtons = document.querySelectorAll('.mode-button');
const navAuthLink = document.querySelector('#nav-auth-link');
const logoutButton = document.querySelector('#logout-button');
const dashboardProfileForm = document.querySelector('#dashboard-profile-form');
const dashboardProfileMessage = document.querySelector('#dashboard-profile-message');
let authMode = 'login';

function initializeApp() {
  populateWeightSelects();
  if (ageGroupSelect) {
    ageGroupSelect.value = '20-30';
  }
  if (currentWeightSelect) {
    currentWeightSelect.value = '70';
  }
  if (desiredWeightSelect) {
    desiredWeightSelect.value = '68';
  }
  if (document.querySelector('#objective')) {
    document.querySelector('#objective').value = 'weight_loss';
  }
  if (modeButtons.length) {
    modeButtons.forEach((button) => {
      button.addEventListener('click', () => setAuthMode(button.dataset.mode));
    });
  }
  if (authForm) {
    authForm.addEventListener('submit', handleAuthSubmit);
  }
  if (logoutButton) {
    logoutButton.addEventListener('click', logout);
  }
  if (dashboardProfileForm) {
    dashboardProfileForm.addEventListener('submit', submitDashboardProfile);
  }
  revealOnScroll();
}

function populateWeightSelects() {
  if (!currentWeightSelect || !desiredWeightSelect) {
    return;
  }

  if (currentWeightSelect.dataset.initialized === 'true') {
    return;
  }
  currentWeightSelect.dataset.initialized = 'true';

  weightOptions.forEach((weight) => {
    const option = new Option(`${weight} kg`, weight);
    currentWeightSelect.add(option);
    desiredWeightSelect.add(option.cloneNode(true));
  });
}

function showMessage(text, isError = false) {
  if (!formMessage) {
    return;
  }
  formMessage.textContent = text;
  formMessage.style.color = isError ? '#ff8d8d' : '#d9e4ff';
}

function showRateLimitMessage(message = 'Muitas tentativas detectadas. Aguarde alguns instantes antes de tentar novamente.') {
  showMessage(message, true);
  if (authMessage) {
    authMessage.textContent = message;
    authMessage.style.color = '#ff8d8d';
  }
}

function setLoadingState(isVisible) {
  if (!loadingSection || !submitButton) {
    return;
  }
  loadingSection.classList.toggle('hidden', !isVisible);
  submitButton.disabled = isVisible;
  submitButton.style.opacity = isVisible ? '0.72' : '1';
  submitButton.style.cursor = isVisible ? 'wait' : 'pointer';
}

function animateLoading() {
  const steps = [
    'Validando informações...',
    'Calculando estimativas...',
    'Montando rotina de treino...',
    'Gerando alimentação sugerida...',
    'Ultimando recomendações...'
  ];

  let index = 0;
  const interval = setInterval(() => {
    index += 1;
    const progress = Math.min(index * 20, 100);
    progressBar.style.width = `${progress}%`;
    loadingMessage.textContent = steps[Math.min(index - 1, steps.length - 1)];

    if (progress >= 100) {
      clearInterval(interval);
    }
  }, 450);
}

function renderPlan(result) {
  document.querySelector('#daily-calories').textContent = `${result.calorias_diarias} kcal`;
  document.querySelector('#protein').textContent = `${result.proteinas} g`;
  document.querySelector('#carbs').textContent = `${result.carboidratos} g`;
  document.querySelector('#fats').textContent = `${result.gorduras} g`;
  document.querySelector('#water').textContent = `${result.agua}`;
  document.querySelector('#time-estimated').textContent = `${result.tempo_estimado}`;

  const resultsTitle = document.querySelector('.results .section-heading h2');
  const objectiveLabel = result.objective_label || formatObjectiveText(result.objective);
  resultsTitle.textContent = `Plano inteligente · ${objectiveLabel}`;

  const mealPlan = document.querySelector('#meal-plan');
  mealPlan.innerHTML = '';
  Object.entries(result.plan_alimentar).forEach(([key, value]) => {
    const li = document.createElement('li');
    li.textContent = `${key.replace(/_/g, ' ')}: ${value}`;
    mealPlan.appendChild(li);
  });

  const trainingPlan = document.querySelector('#training-plan');
  trainingPlan.innerHTML = '';
  Object.entries(result.plano_treino).forEach(([day, info]) => {
    const item = document.createElement('div');
    item.className = 'training-item';
    const label = {
      'segunda-feira': 'SEGUNDA',
      'terça-feira': 'TERÇA',
      'quarta-feira': 'QUARTA',
      'quinta-feira': 'QUINTA',
      'sexta-feira': 'SEXTA',
      'sábado': 'SÁBADO'
    }[day] || day;
    item.innerHTML = `<strong>${label}</strong><br><span class="training-meta">${info.muscle_group}</span><br>Exercícios: ${info.exercise}<br>Séries: ${info.sets}<br>Repetições: ${info.reps}<br>Descanso: ${info.rest}<br>Cardio: ${info.cardio}`;
    trainingPlan.appendChild(item);
  });

  const recommendations = document.querySelector('#recommendations');
  recommendations.innerHTML = '';
  result.recomendacoes.forEach((item) => {
    const li = document.createElement('li');
    li.textContent = item;
    recommendations.appendChild(li);
  });

  const tips = document.querySelector('#tips');
  tips.innerHTML = '';
  result.dicas.forEach((item) => {
    const li = document.createElement('li');
    li.textContent = item;
    tips.appendChild(li);
  });

  const observations = document.querySelector('#observations');
  observations.innerHTML = '';
  result.observacoes.forEach((item) => {
    const li = document.createElement('li');
    li.textContent = item;
    observations.appendChild(li);
  });

  document.querySelector('#responsibility-note').textContent = result.responsibility_note;
  const weeklyRest = document.createElement('li');
  weeklyRest.textContent = `Descanso semanal sugerido: ${result.weekly_rest_time}.`;
  recommendations.appendChild(weeklyRest);
}

function formatObjectiveText(objective) {
  return objective === 'weight_loss'
    ? 'Perda de peso'
    : objective === 'muscle_gain'
      ? 'Ganho de massa muscular'
      : 'Aumento de força';
}

function revealOnScroll() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  }, { threshold: 0.14 });

  document.querySelectorAll('.reveal').forEach((item) => observer.observe(item));
}

function setAuthMode(mode) {
  authMode = mode;
  modeButtons.forEach((button) => {
    button.classList.toggle('active', button.dataset.mode === mode);
  });
  if (authUsernameInput) {
    authUsernameInput.style.display = mode === 'register' ? 'block' : 'none';
  }
  if (authMessage) {
    authMessage.textContent = '';
  }
}

function showAuthMessage(text, isError = false) {
  if (!authMessage) {
    return;
  }
  authMessage.textContent = text;
  authMessage.style.color = isError ? '#ff8d8d' : '#d9e4ff';
}

function showDashboardProfileMessage(text, isError = false) {
  if (!dashboardProfileMessage) {
    return;
  }
  dashboardProfileMessage.textContent = text;
  dashboardProfileMessage.style.color = isError ? '#ff8d8d' : '#d9e4ff';
}

async function handleAuthSubmit(event) {
  event.preventDefault();
  const endpoint = authMode === 'register' ? '/api/auth/register' : '/api/auth/login';
  const payload = {
    username: authUsernameInput ? authUsernameInput.value.trim() : '',
    email: authEmailInput.value.trim(),
    password: authPasswordInput.value,
  };

  if (!payload.email || !payload.password || (authMode === 'register' && !payload.username)) {
    showAuthMessage('Preencha todos os campos da conta.', true);
    return;
  }

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    let data = {};
    try {
      data = await response.json();
    } catch (_error) {
      data = {};
    }

    if (!response.ok) {
      if (response.status === 429) {
        const rateLimitMessage = data.error || 'O site está recebendo muitas tentativas. Aguarde alguns instantes e tente novamente.';
        showRateLimitMessage(rateLimitMessage);
        return;
      }
      throw new Error(data.error || 'Falha ao autenticar.');
    }

    showAuthMessage(data.message || 'Conta conectada.');
    if (navAuthLink) {
      navAuthLink.textContent = 'Dashboard';
      navAuthLink.href = '/dashboard';
    }
    window.location.href = '/dashboard';
  } catch (error) {
    showAuthMessage(error.message, true);
  }
}

async function logout() {
  if (!logoutButton) {
    return;
  }

  try {
    await fetch('/api/auth/logout', { method: 'POST' });
    window.location.href = '/';
  } catch (error) {
    window.location.href = '/';
  }
}

async function submitDashboardProfile(event) {
  if (!dashboardProfileForm) {
    return;
  }

  event.preventDefault();
  const payload = {
    full_name: document.querySelector('#full_name')?.value.trim() || '',
    sex: document.querySelector('#sex')?.value || '',
    age: document.querySelector('#age')?.value || '',
    height_cm: document.querySelector('#height_cm')?.value || '',
    experience_level: document.querySelector('#experience_level')?.value || '',
  };

  try {
    const response = await fetch('/api/profile', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.details ? Object.values(data.details).join(' ') : data.error || 'Não foi possível salvar o perfil.');
    }

    showDashboardProfileMessage('Perfil atualizado com sucesso.');
  } catch (error) {
    showDashboardProfileMessage(error.message || 'Não foi possível salvar o perfil.', true);
  }
}

if (form) {
  form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const payload = {
      age_group: ageGroupSelect ? ageGroupSelect.value : '',
      current_weight: currentWeightSelect ? currentWeightSelect.value : '',
      desired_weight: desiredWeightSelect ? desiredWeightSelect.value : '',
      objective: document.querySelector('#objective') ? document.querySelector('#objective').value : '',
    };

    if (!payload.age_group || !payload.current_weight || !payload.desired_weight || !payload.objective) {
      showMessage('Preencha todos os campos obrigatórios.', true);
      return;
    }

    showMessage('Gerando seu plano, aguarde um momento...');
    setLoadingState(true);
    if (progressBar) {
      progressBar.style.width = '0%';
    }
    animateLoading();
    if (resultsSection) {
      resultsSection.classList.add('hidden');
    }

    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      let data = {};
      try {
        data = await response.json();
      } catch (_error) {
        data = {};
      }

      if (!response.ok) {
        if (response.status === 429) {
          const rateLimitMessage = data.error || 'O site está com muitas tentativas ao mesmo tempo. Aguarde alguns instantes e tente novamente.';
          showRateLimitMessage(rateLimitMessage);
          return;
        }
        throw new Error(data.details ? Object.values(data.details).join(' ') : data.error || 'Erro ao gerar plano.');
      }

      if (!data || !data.result) {
        throw new Error('A resposta do plano foi inválida.');
      }

      renderPlan(data.result);
      if (resultsSection) {
        resultsSection.classList.remove('hidden');
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
      showMessage(data.saved ? 'Plano gerado e salvo no seu histórico.' : 'Plano gerado com sucesso.');
    } catch (error) {
      showMessage(error.message || 'Não foi possível gerar o plano.', true);
    } finally {
      setLoadingState(false);
      if (progressBar) {
        progressBar.style.width = '0%';
      }
    }
  });
}

document.addEventListener('DOMContentLoaded', initializeApp);

if (authForm) {
  authForm.addEventListener('submit', handleAuthSubmit);
}

if (dashboardProfileForm) {
  dashboardProfileForm.addEventListener('submit', submitDashboardProfile);
}

modeButtons.forEach((button) => {
  button.addEventListener('click', () => setAuthMode(button.dataset.mode));
});

if (logoutButton) {
  logoutButton.addEventListener('click', logout);
}

populateWeightSelects();
revealOnScroll();
setAuthMode('login');

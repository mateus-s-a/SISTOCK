/**
 * Sistema de Autocomplete Reutilizável
 * Uso: new Autocomplete(inputElement, apiUrl, options)
 */

class Autocomplete {
    constructor(inputElement, apiUrl, options = {}) {
        this.input = inputElement;
        this.apiUrl = apiUrl;
        this.options = {
            minChars: options.minChars || 2,
            debounceTime: options.debounceTime || 300,
            onSelect: options.onSelect || this.defaultOnSelect.bind(this),
            formatResult: options.formatResult || this.defaultFormatResult.bind(this),
            ...options
        };

        this.debounceTimer = null;
        this.resultsContainer = null;

        this.init();
    }


    init() {
        // Cria container de resultados
        this.createResultsContainer();

        // Adiciona event listeners
        this.input.addEventListener('input', this.handleInput.bind(this));
        this.input.addEventListener('focus', this.handleFocus.bind(this));
        document.addEventListener('click', this.handleClickOutside.bind(this));

        // Adiciona ícone de busca
        this.addSearchIcon();
    }


    createResultsContainer() {
        const wrapper = document.createElement('div');
        wrapper.className = 'autocomplete-container';

        this.resultsContainer = document.createElement('div');
        this.resultsContainer.className = 'autocomplete-results';

        this.input.parentNode.insertBefore(wrapper, this.input);
        wrapper.appendChild(this.input);
        wrapper.appendChild(this.resultsContainer);
    }

    addSearchIcon() {
        const icon = document.createElement('i');
        icon.className = 'fas fa-search autocomplete-icon';
        this.input.parentNode.appendChild(icon);
        this.input.classList.add('autocomplete-input');
    }

    handleInput(e) {
        const query = e.target.value.trim();

        // Limpa timer anterior
        clearTimeout(this.debounceTimer);

        // Se query muito curta, esconde resultados
        if (query.length < this.options.minChars) {
            this.hideResults();
            return;
        }

        // Debounce - espera usuário parar de digitar
        this.debounceTimer = setTimeout(() => {
            this.search(query);
        }, this.options.debounceTime);
    }

    handleFocus() {
        if (this.resultsContainer.children.length > 0) {
            this.showResults();
        }
    }

    handleClickOutside(e) {
        if (!this.input.parentNode.contains(e.target)) {
            this.hideResults();
        }
    }


    async search(query) {
        this.showLoading();

        try {
            const response = await fetch(`${this.apiUrl}?q=${encodeURIComponent(query)}`);
            const data = await response.json();

            this.displayResults(data.results, query);
        } catch (error) {
            console.error('Erro no autocomplete:', error);
            this.showError();
        }
    }

    showLoading() {
        this.resultsContainer.innerHTML = `
            <div class="autocomplete-loading">
                <i class="fas fa-spinner fa-spin"></i> Buscando...
            </div>
        `;
        this.showResults();
    }

    showError() {
        this.resultsContainer.innerHTML = `
            <div class="autocomplete-empty text-danger">
                <i class="fas fa-exclamation-triangle"></i> Erro ao buscar
            </div>
        `;
    }

    displayResults(results, query) {
        if (results.length === 0) {
            this.resultsContainer.innerHTML = `
                <div class="autocomplete-empty">
                    Nenhum resultado encontrado para "${query}"
                </div>
            `;
            this.showResults();
            return;
        }

        this.resultsContainer.innerHTML = '';

        results.forEach(result => {
            const item = document.createElement('div');
            item.className = 'autocomplete-item';
            item.innerHTML = this.options.formatResult(result, query);
            item.addEventListener('click', () => this.selectItem(result));

            this.resultsContainer.appendChild(item);
        });

        this.showResults();
    }

    defaultFormatResult(result, query) {
        // Highlight do termo buscado
        const highlightText = (text) => {
            const regex = new RegExp(`(${query})`, 'gi');
            return text.replace(regex, '<span class="highlight">$1</span>');
        };

        return `
            <div class="autocomplete-item-title">${highlightText(result.name)}</div>
            <div class="autocomplete-item-subtitle">${result.sku || result.email || ''}</div>
        `;
    }

    selectItem(result) {
        this.options.onSelect(result);
        this.hideResults();
    }

    defaultOnSelect(result) {
        // Comportamento padrão: preenche input e redireciona
        this.input.value = result.name;
        if (result.url) {
            window.location.href = result.url;
        }
    }

    showResults() {
        this.resultsContainer.classList.add('show');
    }

    hideResults() {
        this.resultsContainer.classList.remove('show');
    }
}

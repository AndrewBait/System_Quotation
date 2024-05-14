$(document).ready(function() {
    // Mostrar o modal de sucesso se houver mensagens de sucesso
    {% for message in messages %}
        if ("{{ message.tags }}" === "success") {
            $('#successModal').modal('show');
        }
    {% endfor %}

    // Funcionalidade de pesquisa
    $("#searchInput").on("keyup", function() {
        var value = $(this).val().toLowerCase();
        $("#productsTable tbody tr").filter(function() {
            $(this).toggle($(this).data("produto").toLowerCase().indexOf(value) > -1);
        });
    });

    // Funcionalidade de ordenação
    $("#filterSelect").on("change", function() {
        var order = $(this).val();
        var rows = $('#productsTable tbody tr').get();

        rows.sort(function(a, b) {
            var A = $(a).data("produto").toUpperCase();
            var B = $(b).data("produto").toUpperCase();

            if (order === "asc") {
                return A < B ? -1 : A > B ? 1 : 0;
            } else {
                return A > B ? -1 : A < B ? 1 : 0;
            }
        });

        $.each(rows, function(index, row) {
            $('#productsTable tbody').append(row);
        });
    });

    // Configurações da paginação
    const rowsPerPage = 10;
    let currentPage = 1;
    const rows = document.querySelectorAll('#productsTable tbody tr');
    const rowsCount = rows.length;
    const pageCount = Math.ceil(rowsCount / rowsPerPage);
    const pagination = document.getElementById('pagination');

    // Função para exibir uma página específica
    function displayPage(page) {
        const start = (page - 1) * rowsPerPage;
        const end = start + rowsPerPage;

        rows.forEach((row, index) => {
            row.style.display = index >= start && index < end ? '' : 'none';
        });

        currentPage = page;

        document.querySelectorAll('.page-item').forEach(item => {
            item.classList.remove('active');
        });

        const pageItem = document.querySelector(`#page${page}`);
        if (pageItem) {
            pageItem.classList.add('active');
        }

        document.getElementById('prevPage').parentNode.classList.toggle('disabled', currentPage === 1);
        document.getElementById('nextPage').parentNode.classList.toggle('disabled', currentPage === pageCount);
    }

    // Adiciona os itens de paginação
    for (let i = 1; i <= pageCount; i++) {
        const li = document.createElement('li');
        li.className = 'page-item';
        li.innerHTML = `<a class="page-link" href="#" id="page${i}">${i}</a>`;
        li.addEventListener('click', (e) => {
            e.preventDefault();
            displayPage(i);
        });
        pagination.insertBefore(li, document.getElementById('nextPage').parentNode);
    }

    // Eventos dos botões de próxima e anterior
    document.getElementById('prevPage').addEventListener('click', (e) => {
        e.preventDefault();
        if (currentPage > 1) {
            displayPage(currentPage - 1);
        }
    });

    document.getElementById('nextPage').addEventListener('click', (e) => {
        e.preventDefault();
        if (currentPage < pageCount) {
            displayPage(currentPage + 1);
        }
    });

    // Exibe a primeira página ao carregar
    displayPage(1);

    // Confirmação antes de enviar o formulário
    document.getElementById('gerar-pedidos-form').onsubmit = function() {
        const radios = document.querySelectorAll('input[type="radio"][name^="selecao_"]');
        for (let radio of radios) {
            if (radio.checked) {
                console.log(radio.name + ': ' + radio.value);
            }
        }
        return confirm('Você tem certeza que deseja gerar os pedidos para as ofertas selecionadas?');
    };
});

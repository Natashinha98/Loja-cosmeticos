async function cadastrarCliente() {
    const dados = {
        nome: document.getElementById("cliente_nome").value,
        email: document.getElementById("cliente_email").value,
        telefone: document.getElementById("cliente_telefone").value
    };

    await fetch("/clientes/", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(dados)
    });

    limparCampos();
    carregarTudo();
}

async function cadastrarProduto() {
    const dados = {
        nome: document.getElementById("produto_nome").value,
        categoria: document.getElementById("produto_categoria").value,
        preco: document.getElementById("produto_preco").value,
        estoque: document.getElementById("produto_estoque").value,
        descricao: document.getElementById("produto_descricao").value
    };

    await fetch("/produtos/", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(dados)
    });

    limparCampos();
    carregarTudo();
}

async function criarPedido() {
    const dados = {
        id_cliente: document.getElementById("pedido_cliente").value,
        id_produto: document.getElementById("pedido_produto").value,
        quantidade: document.getElementById("pedido_quantidade").value
    };

    await fetch("/pedidos/", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(dados)
    });

    limparCampos();
    carregarTudo();
}

async function carregarClientes() {
    const resposta = await fetch("/clientes/");
    const clientes = await resposta.json();

    const div = document.getElementById("lista_clientes");
    div.innerHTML = "";

    clientes.forEach(cliente => {
        div.innerHTML += `
            <div class="item">
                <b>${cliente.nome}</b>
                <div class="pequeno">ID: ${cliente.id_cliente} | ${cliente.email} | ${cliente.telefone || ""}</div>
            </div>
        `;
    });
}

async function carregarProdutos() {
    const resposta = await fetch("/produtos/");
    const produtos = await resposta.json();

    const div = document.getElementById("lista_produtos");
    const select = document.getElementById("pedido_produto");

    div.innerHTML = "";
    select.innerHTML = "";

    produtos.forEach(produto => {
        div.innerHTML += `
            <div class="item">
                <b>${produto.nome}</b> - R$ ${produto.preco}
                <div class="pequeno">ID: ${produto.id_produto} | ${produto.categoria} | estoque: ${produto.estoque}</div>
                <div>${produto.descricao || ""}</div>
            </div>
        `;

        select.innerHTML += `<option value="${produto.id_produto}">${produto.nome} - R$ ${produto.preco}</option>`;
    });
}

async function carregarPedidos() {
    const resposta = await fetch("/pedidos/");
    const pedidos = await resposta.json();

    const div = document.getElementById("lista_pedidos");
    div.innerHTML = "";

    pedidos.forEach(pedido => {
        div.innerHTML += `
            <div class="item">
                <b>Pedido ${pedido.id_pedido}</b> - ${pedido.nome_produto}
                <div class="pequeno">Cliente: ${pedido.id_cliente} | qtd: ${pedido.quantidade} | total: R$ ${pedido.total} | status: ${pedido.status}</div>
            </div>
        `;
    });
}

function limparCampos() {
    document.querySelectorAll("input").forEach(input => {
        if (input.id !== "pedido_quantidade") {
            input.value = "";
        }
    });
    document.getElementById("pedido_quantidade").value = 1;
}

function carregarTudo() {
    carregarClientes();
    carregarProdutos();
    carregarPedidos();
}

carregarTudo();

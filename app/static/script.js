let clientesSalvos = [];
let produtosSalvos = [];
let pedidosSalvos = [];

let clienteEditando = null;
let produtoEditando = null;
let pedidoEditando = null;

function dinheiro(valor) {
    return Number(valor).toFixed(2).replace(".", ",");
}

// ================= CLIENTES =================

async function criarCliente() {
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

    document.getElementById("cliente_nome").value = "";
    document.getElementById("cliente_email").value = "";
    document.getElementById("cliente_telefone").value = "";

    carregarTudo();
}

async function salvarClienteEditado(idCliente) {
    const dados = {
        nome: document.getElementById(`editar_cliente_nome_${idCliente}`).value,
        email: document.getElementById(`editar_cliente_email_${idCliente}`).value,
        telefone: document.getElementById(`editar_cliente_telefone_${idCliente}`).value
    };

    await fetch(`/clientes/${idCliente}`, {
        method: "PUT",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(dados)
    });

    clienteEditando = null;
    carregarTudo();
}

async function apagarCliente(idCliente) {
    await fetch(`/clientes/${idCliente}`, {
        method: "DELETE"
    });

    carregarTudo();
}

function editarCliente(idCliente) {
    clienteEditando = idCliente;
    carregarClientes();
}

function cancelarEdicaoCliente() {
    clienteEditando = null;
    carregarClientes();
}

// ================= PRODUTOS =================

async function criarProduto() {
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

    document.getElementById("produto_nome").value = "";
    document.getElementById("produto_categoria").value = "";
    document.getElementById("produto_preco").value = "";
    document.getElementById("produto_estoque").value = "";
    document.getElementById("produto_descricao").value = "";

    carregarTudo();
}

async function salvarProdutoEditado(idProduto) {
    const dados = {
        nome: document.getElementById(`editar_produto_nome_${idProduto}`).value,
        categoria: document.getElementById(`editar_produto_categoria_${idProduto}`).value,
        preco: document.getElementById(`editar_produto_preco_${idProduto}`).value,
        estoque: document.getElementById(`editar_produto_estoque_${idProduto}`).value,
        descricao: document.getElementById(`editar_produto_descricao_${idProduto}`).value
    };

    await fetch(`/produtos/${idProduto}`, {
        method: "PUT",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(dados)
    });

    produtoEditando = null;
    carregarTudo();
}

async function apagarProduto(idProduto) {
    await fetch(`/produtos/${idProduto}`, {
        method: "DELETE"
    });

    carregarTudo();
}

function editarProduto(idProduto) {
    produtoEditando = idProduto;
    carregarProdutos();
}

function cancelarEdicaoProduto() {
    produtoEditando = null;
    carregarProdutos();
}

// ================= PEDIDOS =================

function pegarProdutosMarcadosCriacao() {
    const itens = [];

    document.querySelectorAll(".produto_marcado_criar").forEach(caixa => {
        if (caixa.checked) {
            const idProduto = caixa.value;
            const quantidade = document.getElementById(`qtd_criar_${idProduto}`).value;

            itens.push({
                id_produto: idProduto,
                quantidade: quantidade
            });
        }
    });

    return itens;
}

function pegarProdutosMarcadosEdicao(idPedido) {
    const itens = [];

    document.querySelectorAll(`.produto_marcado_editar_${idPedido}`).forEach(caixa => {
        if (caixa.checked) {
            const idProduto = caixa.value;
            const quantidade = document.getElementById(`qtd_editar_${idPedido}_${idProduto}`).value;

            itens.push({
                id_produto: idProduto,
                quantidade: quantidade
            });
        }
    });

    return itens;
}

async function criarPedido() {
    const dados = {
        id_cliente: document.getElementById("pedido_cliente").value,
        status: document.getElementById("pedido_status").value,
        itens: pegarProdutosMarcadosCriacao()
    };

    if (dados.itens.length === 0) {
        alert("Escolha pelo menos um produto para o pedido.");
        return;
    }

    await fetch("/pedidos/", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(dados)
    });

    document.getElementById("pedido_status").value = "criado";

    document.querySelectorAll(".produto_marcado_criar").forEach(caixa => {
        caixa.checked = false;
    });

    document.querySelectorAll(".quantidade_produto").forEach(input => {
        input.value = 1;
    });

    carregarTudo();
}

async function salvarPedidoEditado(idPedido) {
    const dados = {
        id_cliente: document.getElementById(`editar_pedido_cliente_${idPedido}`).value,
        status: document.getElementById(`editar_pedido_status_${idPedido}`).value,
        itens: pegarProdutosMarcadosEdicao(idPedido)
    };

    if (dados.itens.length === 0) {
        alert("Escolha pelo menos um produto para o pedido.");
        return;
    }

    await fetch(`/pedidos/${idPedido}`, {
        method: "PUT",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(dados)
    });

    pedidoEditando = null;
    carregarTudo();
}

async function apagarPedido(idPedido) {
    await fetch(`/pedidos/${idPedido}`, {
        method: "DELETE"
    });

    carregarTudo();
}

function editarPedido(idPedido) {
    pedidoEditando = idPedido;
    carregarPedidos();
}

function cancelarEdicaoPedido() {
    pedidoEditando = null;
    carregarPedidos();
}

// ================= CARREGAR LISTAS =================

async function carregarClientes() {
    const resposta = await fetch("/clientes/");
    const clientes = await resposta.json();

    clientesSalvos = clientes;

    const div = document.getElementById("lista_clientes");
    const selectCliente = document.getElementById("pedido_cliente");

    div.innerHTML = "";
    selectCliente.innerHTML = "";

    clientes.forEach(cliente => {
        selectCliente.innerHTML += `
            <option value="${cliente.id_cliente}">
                ${cliente.nome}
            </option>
        `;

        if (clienteEditando === cliente.id_cliente) {
            div.innerHTML += `
                <div class="item editando">
                    <input id="editar_cliente_nome_${cliente.id_cliente}" value="${cliente.nome}">
                    <input id="editar_cliente_email_${cliente.id_cliente}" value="${cliente.email}">
                    <input id="editar_cliente_telefone_${cliente.id_cliente}" value="${cliente.telefone || ""}">

                    <div class="acoes">
                        <button onclick="salvarClienteEditado(${cliente.id_cliente})">Salvar</button>
                        <button class="botao_secundario" onclick="cancelarEdicaoCliente()">Cancelar</button>
                    </div>
                </div>
            `;
        } else {
            div.innerHTML += `
                <div class="item">
                    <b>${cliente.nome}</b>
                    <div class="pequeno">${cliente.email} | ${cliente.telefone || ""}</div>

                    <div class="acoes">
                        <button onclick="editarCliente(${cliente.id_cliente})">Editar</button>
                        <button class="botao_perigo" onclick="apagarCliente(${cliente.id_cliente})">Apagar</button>
                    </div>
                </div>
            `;
        }
    });
}

async function carregarProdutos() {
    const resposta = await fetch("/produtos/");
    const produtos = await resposta.json();

    produtosSalvos = produtos;

    const div = document.getElementById("lista_produtos");
    const areaPedido = document.getElementById("area_produtos_pedido");

    div.innerHTML = "";
    areaPedido.innerHTML = "";

    produtos.forEach(produto => {
        areaPedido.innerHTML += `
            <div class="produto_pedido">
                <label>
                    <input class="produto_marcado_criar" type="checkbox" value="${produto.id_produto}">
                    ${produto.nome} - R$ ${dinheiro(produto.preco)}
                </label>

                <input
                    id="qtd_criar_${produto.id_produto}"
                    class="quantidade_produto"
                    type="number"
                    min="1"
                    value="1"
                    placeholder="Qtd"
                >
            </div>
        `;

        if (produtoEditando === produto.id_produto) {
            div.innerHTML += `
                <div class="item editando">
                    <input id="editar_produto_nome_${produto.id_produto}" value="${produto.nome}">
                    <input id="editar_produto_categoria_${produto.id_produto}" value="${produto.categoria}">
                    <input id="editar_produto_preco_${produto.id_produto}" type="number" step="0.01" value="${produto.preco}">
                    <input id="editar_produto_estoque_${produto.id_produto}" type="number" value="${produto.estoque}">
                    <input id="editar_produto_descricao_${produto.id_produto}" value="${produto.descricao || ""}">

                    <div class="acoes">
                        <button onclick="salvarProdutoEditado('${produto.id_produto}')">Salvar</button>
                        <button class="botao_secundario" onclick="cancelarEdicaoProduto()">Cancelar</button>
                    </div>
                </div>
            `;
        } else {
            div.innerHTML += `
                <div class="item">
                    <b>${produto.nome}</b> - R$ ${dinheiro(produto.preco)}
                    <div class="pequeno">${produto.categoria} | estoque: ${produto.estoque}</div>
                    <div>${produto.descricao || ""}</div>

                    <div class="acoes">
                        <button onclick="editarProduto('${produto.id_produto}')">Editar</button>
                        <button class="botao_perigo" onclick="apagarProduto('${produto.id_produto}')">Apagar</button>
                    </div>
                </div>
            `;
        }
    });
}

async function carregarPedidos() {
    const resposta = await fetch("/pedidos/");
    const pedidos = await resposta.json();

    pedidosSalvos = pedidos;

    const div = document.getElementById("lista_pedidos");
    div.innerHTML = "";

    pedidos.forEach(pedido => {
        if (pedidoEditando === pedido.id_pedido) {
            div.innerHTML += montarPedidoEditavel(pedido);
        } else {
            div.innerHTML += `
                <div class="item">
                    <b>Pedido ${pedido.id_pedido}</b>
                    <div>Cliente: ${pedido.nome_cliente}</div>
                    <div>Produtos: ${pedido.resumo_produtos}</div>
                    <div class="pequeno">
                        Quantidade total: ${pedido.quantidade_total} |
                        Total: R$ ${dinheiro(pedido.total)} |
                        Status: ${pedido.status}
                    </div>

                    <div class="acoes">
                        <button onclick="editarPedido(${pedido.id_pedido})">Editar</button>
                        <button class="botao_perigo" onclick="apagarPedido(${pedido.id_pedido})">Apagar</button>
                    </div>
                </div>
            `;
        }
    });
}

function montarPedidoEditavel(pedido) {
    let opcoesClientes = "";

    clientesSalvos.forEach(cliente => {
        const selecionado = cliente.id_cliente === pedido.id_cliente ? "selected" : "";

        opcoesClientes += `
            <option value="${cliente.id_cliente}" ${selecionado}>
                ${cliente.nome}
            </option>
        `;
    });

    let produtosEditaveis = "";

    produtosSalvos.forEach(produto => {
        const produtoNoPedido = pedido.produtos.find(p => p.id_produto === produto.id_produto);
        const marcado = produtoNoPedido ? "checked" : "";
        const quantidade = produtoNoPedido ? produtoNoPedido.quantidade : 1;

        produtosEditaveis += `
            <div class="produto_pedido">
                <label>
                    <input
                        class="produto_marcado_editar_${pedido.id_pedido}"
                        type="checkbox"
                        value="${produto.id_produto}"
                        ${marcado}
                    >
                    ${produto.nome} - R$ ${dinheiro(produto.preco)}
                </label>

                <input
                    id="qtd_editar_${pedido.id_pedido}_${produto.id_produto}"
                    class="quantidade_produto"
                    type="number"
                    min="1"
                    value="${quantidade}"
                >
            </div>
        `;
    });

    return `
        <div class="item editando">
            <b>Editando pedido ${pedido.id_pedido}</b>

            <label>Cliente:</label>
            <select id="editar_pedido_cliente_${pedido.id_pedido}">
                ${opcoesClientes}
            </select>

            <label>Status:</label>
            <select id="editar_pedido_status_${pedido.id_pedido}">
                <option value="criado" ${pedido.status === "criado" ? "selected" : ""}>Criado</option>
                <option value="pago" ${pedido.status === "pago" ? "selected" : ""}>Pago</option>
                <option value="enviado" ${pedido.status === "enviado" ? "selected" : ""}>Enviado</option>
                <option value="cancelado" ${pedido.status === "cancelado" ? "selected" : ""}>Cancelado</option>
            </select>

            <h3>Produtos do pedido</h3>
            ${produtosEditaveis}

            <div class="acoes">
                <button onclick="salvarPedidoEditado(${pedido.id_pedido})">Salvar</button>
                <button class="botao_secundario" onclick="cancelarEdicaoPedido()">Cancelar</button>
            </div>
        </div>
    `;
}

async function carregarTudo() {
    await carregarClientes();
    await carregarProdutos();
    await carregarPedidos();
}

carregarTudo();
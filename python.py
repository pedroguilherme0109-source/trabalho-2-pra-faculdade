"""
Estudo de caso: sistema de gerenciamento de uma locadora de veículos.

Classes identificadas:
    Veiculo (superclasse), Carro, Moto e Caminhao;
    Cliente (superclasse), PessoaFisica e PessoaJuridica;
    ContratoLocacao, Condutor e Manutencao.

Generalizacao/especializacao:
    Carro, Moto e Caminhao especializam Veiculo.
    PessoaFisica e PessoaJuridica especializam Cliente.

Relacionamentos:
    Cliente -- ContratoLocacao: associacao. Um contrato referencia um cliente;
    o cliente pode participar de varios contratos ao longo do tempo.
    Veiculo -- ContratoLocacao: associacao. O contrato referencia um veiculo;
    o veiculo pode ter varios contratos historicos, mas no maximo um ativo.
    ContratoLocacao *-- Condutor: composicao. O contrato instancia seu condutor,
    que nao tem existencia independente no dominio descrito.
    Veiculo -- Manutencao: associacao. Cada manutencao referencia um veiculo e
    compoe seu historico, mas o enunciado nao determina que ela seja excluida
    junto com o veiculo; por isso nao se presume composicao.

Nao ha agregacao claramente estabelecida no enunciado: nao se descreve um
relacionamento todo-parte com ciclo de vida independente suficiente para isso.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date


class Veiculo(ABC):
    def __init__(self, placa: str, modelo: str, ano: int, valor_diaria: float) -> None:
        if valor_diaria < 0:
            raise ValueError("O valor da diaria nao pode ser negativo.")

        self.placa = placa
        self.modelo = modelo
        self.ano = ano
        self.valor_diaria = valor_diaria
        self._contrato_ativo: ContratoLocacao | None = None
        self.manutencoes: list[Manutencao] = []

    def esta_disponivel(self) -> bool:
        return self._contrato_ativo is None

    def registrar_contrato(self, contrato: ContratoLocacao) -> None:
        if not self.esta_disponivel():
            raise ValueError("O veiculo ja possui um contrato ativo.")
        self._contrato_ativo = contrato

    def liberar_contrato(self, contrato: ContratoLocacao) -> None:
        if self._contrato_ativo is not contrato:
            raise ValueError("O contrato informado nao e o contrato ativo do veiculo.")
        self._contrato_ativo = None

    def registrar_manutencao(
        self, data: date, tipo_servico: str, custo: float
    ) -> Manutencao:
        manutencao = Manutencao(data, tipo_servico, custo, self)
        self.manutencoes.append(manutencao)
        return manutencao

    @abstractmethod
    def descrever(self) -> str:
        """Retorna uma descricao do veiculo e de suas caracteristicas."""

    @abstractmethod
    def validar_categoria(self) -> bool:
        """Indica se as caracteristicas especificas da categoria sao validas."""


class Carro(Veiculo):
    def __init__(
        self,
        placa: str,
        modelo: str,
        ano: int,
        valor_diaria: float,
        quantidade_portas: int,
        capacidade_passageiros: int,
        cambio_automatico: bool,
    ) -> None:
        super().__init__(placa, modelo, ano, valor_diaria)
        self.quantidade_portas = quantidade_portas
        self.capacidade_passageiros = capacidade_passageiros
        self.cambio_automatico = cambio_automatico

    def descrever(self) -> str:
        cambio = "automatico" if self.cambio_automatico else "manual"
        return (
            f"Carro {self.modelo}, placa {self.placa}, "
            f"{self.quantidade_portas} portas, cambio {cambio}."
        )

    def validar_categoria(self) -> bool:
        return self.quantidade_portas > 0 and self.capacidade_passageiros > 0


class Moto(Veiculo):
    def __init__(
        self,
        placa: str,
        modelo: str,
        ano: int,
        valor_diaria: float,
        cilindradas: int,
        tipo: str,
        partida_eletrica: bool,
    ) -> None:
        super().__init__(placa, modelo, ano, valor_diaria)
        self.cilindradas = cilindradas
        self.tipo = tipo
        self.partida_eletrica = partida_eletrica

    def descrever(self) -> str:
        partida = "eletrica" if self.partida_eletrica else "a pedal"
        return (
            f"Moto {self.modelo}, placa {self.placa}, "
            f"{self.cilindradas} cc, partida {partida}."
        )

    def validar_categoria(self) -> bool:
        return self.cilindradas > 0 and bool(self.tipo.strip())


class Caminhao(Veiculo):
    def __init__(
        self,
        placa: str,
        modelo: str,
        ano: int,
        valor_diaria: float,
        capacidade_carga_toneladas: float,
        quantidade_eixos: int,
        refrigerado: bool,
    ) -> None:
        super().__init__(placa, modelo, ano, valor_diaria)
        self.capacidade_carga_toneladas = capacidade_carga_toneladas
        self.quantidade_eixos = quantidade_eixos
        self.refrigerado = refrigerado

    def descrever(self) -> str:
        carga = "refrigerada" if self.refrigerado else "seca"
        return (
            f"Caminhao {self.modelo}, placa {self.placa}, "
            f"{self.capacidade_carga_toneladas} t, carga {carga}."
        )

    def validar_categoria(self) -> bool:
        return self.capacidade_carga_toneladas > 0 and self.quantidade_eixos > 0


class Cliente(ABC):
    def __init__(self, nome: str, documento: str, telefone: str) -> None:
        self.nome = nome
        self.documento = documento
        self.telefone = telefone

    def atualizar_telefone(self, telefone: str) -> None:
        self.telefone = telefone

    @abstractmethod
    def validar_documento(self) -> bool:
        """Valida o formato e o comprimento do documento do cliente."""

    @abstractmethod
    def tipo_cliente(self) -> str:
        """Retorna a categoria do cliente."""


class PessoaFisica(Cliente):
    def __init__(
        self, nome: str, cpf: str, telefone: str, data_nascimento: date
    ) -> None:
        super().__init__(nome, cpf, telefone)
        self.data_nascimento = data_nascimento

    def validar_documento(self) -> bool:
        digitos = "".join(caractere for caractere in self.documento if caractere.isdigit())
        return len(digitos) == 11

    def tipo_cliente(self) -> str:
        return "Pessoa fisica"


class PessoaJuridica(Cliente):
    def __init__(
        self,
        razao_social: str,
        cnpj: str,
        telefone: str,
        nome_fantasia: str,
    ) -> None:
        super().__init__(razao_social, cnpj, telefone)
        self.nome_fantasia = nome_fantasia

    def validar_documento(self) -> bool:
        digitos = "".join(caractere for caractere in self.documento if caractere.isdigit())
        return len(digitos) == 14

    def tipo_cliente(self) -> str:
        return "Pessoa juridica"


class Condutor:
    def __init__(self, nome: str, cnh: str) -> None:
        self.nome = nome
        self.cnh = cnh
        self.categoria_cnh = ""

    def atualizar_cnh(self, cnh: str, categoria: str) -> None:
        self.cnh = cnh
        self.categoria_cnh = categoria

    def identificacao(self) -> str:
        return f"{self.nome} (CNH: {self.cnh})"


class ContratoLocacao:
    STATUS_ATIVO = "ativo"
    STATUS_FINALIZADO = "finalizado"
    STATUS_CANCELADO = "cancelado"

    def __init__(
        self,
        cliente: Cliente,
        veiculo: Veiculo,
        data_inicio: date,
        data_termino_prevista: date,
        condutor_nome: str,
        condutor_cnh: str,
    ) -> None:
        if data_termino_prevista < data_inicio:
            raise ValueError("A data de termino nao pode anteceder a data de inicio.")

        self.cliente = cliente
        self.veiculo = veiculo
        self.data_inicio = data_inicio
        self.data_termino_prevista = data_termino_prevista
        self.valor_total = veiculo.valor_diaria * max(
            1, (data_termino_prevista - data_inicio).days
        )
        self._status = self.STATUS_ATIVO
        # O contrato cria e controla o ciclo de vida do condutor (composicao).
        self.condutor = Condutor(condutor_nome, condutor_cnh)
        veiculo.registrar_contrato(self)

    @property
    def status(self) -> str:
        return self._status

    def finalizar(self) -> None:
        self._encerrar(self.STATUS_FINALIZADO)

    def cancelar(self) -> None:
        self._encerrar(self.STATUS_CANCELADO)

    def _encerrar(self, novo_status: str) -> None:
        if self._status != self.STATUS_ATIVO:
            raise ValueError("Somente um contrato ativo pode ser encerrado.")
        self._status = novo_status
        self.veiculo.liberar_contrato(self)

    def resumo(self) -> str:
        return (
            f"Contrato {self.status}: {self.cliente.nome} - "
            f"{self.veiculo.placa}, total R$ {self.valor_total:.2f}."
        )


class Manutencao:
    def __init__(
        self, data: date, tipo_servico: str, custo: float, veiculo: Veiculo
    ) -> None:
        if custo < 0:
            raise ValueError("O custo da manutencao nao pode ser negativo.")

        self.data = data
        self.tipo_servico = tipo_servico
        self.custo = custo
        self.veiculo = veiculo

    def atualizar_custo(self, custo: float) -> None:
        if custo < 0:
            raise ValueError("O custo da manutencao nao pode ser negativo.")
        self.custo = custo

    def descricao(self) -> str:
        return (
            f"{self.data.isoformat()}: {self.tipo_servico} no veiculo "
            f"{self.veiculo.placa}, custo R$ {self.custo:.2f}."
        )


if __name__ == "__main__":
    cliente = PessoaFisica(
        "Ana Silva", "123.456.789-00", "(11) 99999-0000", date(1995, 5, 10)
    )
    carro = Carro("ABC1D23", "Hatch", 2024, 150.0, 4, 5, False)
    contrato = ContratoLocacao(
        cliente,
        carro,
        date(2026, 10, 5),
        date(2026, 10, 8),
        "Carlos Souza",
        "12345678900",
    )
    manutencao = carro.registrar_manutencao(
        date(2026, 9, 20), "Revisao", 350.0
    )

    print(carro.descrever())
    print(contrato.resumo())
    print(f"Condutor do contrato: {contrato.condutor.identificacao()}")
    print(manutencao.descricao())
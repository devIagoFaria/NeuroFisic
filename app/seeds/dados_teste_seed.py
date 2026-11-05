
import random
from datetime import date, timedelta

from faker import Faker

from app import create_app, db
from app.models.profissional import Profissional
from app.models.paciente import Paciente
from app.models.avaliacao import Avaliacao
from app.models.ravlt import RAVLT
from app.models.tmt import TMT
from app.models.fluencia_verbal import FluenciaVerbal


fake = Faker("pt_BR")
random.seed(42)
Faker.seed(42)


def limitar(valor, minimo, maximo):
    return max(minimo, min(maximo, int(round(valor))))


def popular_banco():

    app = create_app()

    with app.app_context():

        profissional = Profissional.query.filter_by(
            email="admin@neuropsico.com"
        ).first()

        if not profissional:
            print("Profissional não encontrado.")
            return

        # Evita duplicar os dados ao executar novamente
        pacientes_existentes = Paciente.query.filter(
            Paciente.nome.like("TESTE_%")
        ).count()

        if pacientes_existentes:
            print("Já existem pacientes de teste.")
            return

        for i in range(100):

            # Fator fictício compartilhado entre os testes.
            # Cria associações artificiais para testar análises.
            desempenho = random.gauss(0, 1)

            idade = random.randint(40, 85)

            paciente = Paciente(
                nome=f"TESTE_{fake.name()}",
                data_nascimento=date.today()
                - timedelta(days=idade * 365),
                sexo=random.choice(["Masculino", "Feminino"]),
                anos_estudo=random.randint(4, 20)
            )

            db.session.add(paciente)
            db.session.flush()

            avaliacao = Avaliacao(
                paciente_id=paciente.id,
                profissional_id=profissional.id,
                data=date.today()
                - timedelta(days=random.randint(0, 365)),
                queixa_atual="Registro fictício para testes.",
                horas_sono_anterior=random.randint(5, 9),
                observacao="Dados gerados automaticamente."
            )

            db.session.add(avaliacao)
            db.session.flush()

            # RAVLT
            a1 = limitar(
                5 + desempenho * 1.5 + random.gauss(0, 1),
                0, 15
            )

            a2 = limitar(
                a1 + random.randint(1, 3),
                0, 15
            )

            a3 = limitar(a2 + random.randint(0, 3), 0, 15)
            a4 = limitar(a3 + random.randint(0, 2), 0, 15)
            a5 = limitar(a4 + random.randint(0, 2), 0, 15)

            ravlt = RAVLT(
                avaliacao_id=avaliacao.id,
                quantidade_a1=a1,
                quantidade_a2=a2,
                quantidade_a3=a3,
                quantidade_a4=a4,
                quantidade_a5=a5,
                quantidade_lista_b=limitar(
                    5 + desempenho,
                    0, 15
                ),
                quantidade_a6=limitar(
                    a5 - random.randint(0, 3),
                    0, 15
                ),
                quantidade_a7=limitar(
                    a5 - random.randint(0, 4),
                    0, 15
                ),
                reconhecimento=limitar(
                    10 + desempenho * 2,
                    0, 15
                )
            )

            # TMT
            tmt = TMT(
                avaliacao_id=avaliacao.id,
                tempo_a=limitar(
                    55 - desempenho * 12
                    + random.gauss(0, 8),
                    15, 180
                ),
                erros_a=random.randint(0, 3),
                tempo_b=limitar(
                    120 - desempenho * 25
                    + random.gauss(0, 15),
                    30, 300
                ),
                erros_b=random.randint(0, 5)
            )

            # Fluência Verbal
            # Fluência Verbal
            respostas_validas = limitar(
                15 + desempenho * 4 + random.gauss(0, 2),
                0, 40
            )

            repeticoes = random.randint(0, 3)

            total_palavras = respostas_validas + repeticoes

            # Distribuição das respostas válidas
            # entre os quatro intervalos de 15 segundos
            palavras_0_15 = respostas_validas // 4
            palavras_16_30 = respostas_validas // 4
            palavras_31_45 = respostas_validas // 4

            palavras_46_60 = (
                respostas_validas
                - palavras_0_15
                - palavras_16_30
                - palavras_31_45
            )

            fluencia = FluenciaVerbal(
                avaliacao_id=avaliacao.id,
                total_palavras=total_palavras,
                respostas_validas=respostas_validas,
                repeticoes=repeticoes,
                palavras_0_15=palavras_0_15,
                palavras_16_30=palavras_16_30,
                palavras_31_45=palavras_31_45,
                palavras_46_60=palavras_46_60
            )

            db.session.add_all([
                ravlt,
                tmt,
                fluencia
            ])

        db.session.commit()

        print("100 pacientes fictícios criados!")
        print("100 avaliações criadas!")
        print("100 resultados RAVLT criados!")
        print("100 resultados TMT criados!")
        print("100 resultados Fluência Verbal criados!")


if __name__ == "__main__":
    popular_banco()

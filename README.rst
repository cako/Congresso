Congresso
=========

O presente projeto tem o objetivo de trazer os dados do Congresso Nacional do Brasil à comunidade Python. Ambas Casas do Congresso, o Senado Federal e a Câmara dos Deputados disponibilizam através de diferentes APIs dados sobre seus parlamentares, matérias, legislaturas, votações, etc. Este módulo tem por finalidade apresentar uma interface unificada para estas informações, facilitando o acesso programático dos dados.

No momento, o projeto ainda está em ativo desenvolvimento, em pré-alpha, com poucos dos recursos das APIs ainda mapeados. Estes recursos somente estão disponíveis para o Senado, e estão descritos abaixo.

Senado
------

O Senado Federal do Brasil disponibiliza seus dados atráves de uma interface REST no portal `Serviços de dados abertos do Senado Federal <http://legis.senado.gov.br/dadosabertos/docs/index.html/>`_. Neste portal, há uma séries de recursos disponíveis, dos quais mapeei ainda alguns poucos, incluindo o /senador/{codigo}/historico e /senador/lista/legislatura/{legislatura}. Com estes recursos foi possível estabelecer as classes Senador, Legislatura, Matéria e Mandato. O uso das mesmas será descrito em uma série de notebooks no formato Jupyter. Os primeiros da série podem ser encontrados no código fonte. Sua visualização pode ser feita através destes links:

1. `Introdução ao congresso.senado <https%3A%2F%2Fbitbucket.org%2Fcdacosta%2Fcongresso%2Fraw%2Fmaster%2Fcongresso%2Fsenado%2Fnotebooks%2Fhtml%2F1.%20Introdu%C3%A7%C3%A3o%20ao%20congresso.senado.html/>`_
2. `Explorando o congresso.senado <https%3A%2F%2Fbitbucket.org%2Fcdacosta%2Fcongresso%2Fraw%2Fmaster%2Fcongresso%2Fsenado%2Fnotebooks%2Fhtml%2F2.%20Explorando%20o%20congresso.senado.html/>`_

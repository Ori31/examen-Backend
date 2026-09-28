from typing import List, Optional
import strawberry


@strawberry.type
class Instructor:
    nombre: str


@strawberry.type
class Taller:
    nombre: str
    instructor: Instructor
    cupo: int
    activo: bool


@strawberry.input
class AgregarTallerInput:
    nombre: str
    instructor: str
    cupo: int
    activo: bool


talleres_db: List[Taller] = [
    
    Taller(
        nombre="Python para backend",
        instructor=Instructor(nombre="Pedro"),
        cupo=20,
        activo=True,
    ),
    Taller(
        nombre="Introducción a Docker",
        instructor=Instructor(nombre="Didier"),
        cupo=15,
        activo=False,
    ),
    Taller(
        nombre="Consultas con GraphQL",
        instructor=Instructor(nombre="Francisco"),
        cupo=25,
        activo=True,
    ),
]


@strawberry.type
class Query:
    @strawberry.field
    def talleres(self) -> List[Taller]:
        return talleres_db

    @strawberry.field
    def taller(self, nombre: str) -> Optional[Taller]:
        for item in talleres_db:
            if item.nombre == nombre:
                return item
        return None

    @strawberry.field
    def talleres_activos(self) -> List[Taller]:
        return [item for item in talleres_db if item.activo]


@strawberry.type
class Mutation:
    @strawberry.mutation
    def agregar_taller(self, taller: AgregarTallerInput) -> Taller:
        nuevo_instructor = Instructor(nombre=taller.instructor)
        nuevo_taller = Taller(
            nombre=taller.nombre,
            instructor=nuevo_instructor,
            cupo=taller.cupo,
            activo=taller.activo,
        )
        talleres_db.append(nuevo_taller)
        return nuevo_taller


schema = strawberry.Schema(query=Query, mutation=Mutation)

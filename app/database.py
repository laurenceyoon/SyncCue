from mongoengine import (
    Document,
    EmbeddedDocument,
    EmbeddedDocumentListField,
    FloatField,
    IntField,
    StringField,
    connect,
)

from app.config import MONGODB_HOST, MONGODB_PORT

connect("synccue", host=MONGODB_HOST, port=MONGODB_PORT)

# ================== schema ==================


class SubPiece(EmbeddedDocument):
    midi_path = StringField(required=True)
    end_time_margin = FloatField(required=True, default=0.0)

    def __str__(self):
        return f"SubPiece({self.midi_path})"


class Piece(Document):
    title = StringField(required=True)
    composer = StringField(required=True)
    midi_path = StringField(required=True)
    subpieces = EmbeddedDocumentListField(SubPiece)
    number = IntField(required=True, default=0)

    def __str__(self):
        return f"Piece({self.title}), number: {self.number}"


# ================== CRUD ==================


def get_piece_list():
    return (
        Piece.objects.all()
        .values_list("number", "title", "composer", "midi_path", "id")
        .order_by("number")
    )


def get_piece_by_id(piece_id):
    return Piece.objects(id=piece_id).first()


def insert_piece(title, composer, midi_path, number):
    piece = Piece(
        title=title,
        composer=composer,
        midi_path=midi_path,
        number=number,
    )
    piece.save()
    return piece


def update_piece(piece_id, title, composer, midi_path, number) -> Piece:
    piece = Piece.objects(id=piece_id).first()
    piece.title = title
    piece.composer = composer
    piece.midi_path = midi_path
    piece.number = number
    piece.save()
    return piece

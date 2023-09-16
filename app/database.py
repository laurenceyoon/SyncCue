from mongoengine import Document, StringField, IntField, connect  # mongoDB

MONGODB_HOST = "0.0.0.0"
MONGODB_PORT = 27017

connect("synccue", host=MONGODB_HOST, port=MONGODB_PORT)

# ================== schema ==================


class Piece(Document):
    title = StringField(required=True)
    composer = StringField(required=True)
    midi_path = StringField(required=True)
    audio_path = StringField(required=True)
    order = IntField(required=True)


# ================== CRUD ==================


def get_piece_list() -> dict:
    return Piece.objects.all()


def get_piece_by_id(piece_id):
    return Piece.objects(id=piece_id).first()


def insert_piece(title, composer, midi_path, audio_path, order):
    piece = Piece(
        title=title,
        composer=composer,
        midi_path=midi_path,
        audio_path=audio_path,
        order=order,
    )
    piece.save()
    return piece


def update_piece(piece_id, title, composer, midi_path, audio_path, order) -> Piece:
    piece = Piece.objects(id=piece_id).first()
    piece.title = title
    piece.composer = composer
    piece.midi_path = midi_path
    piece.audio_path = audio_path
    piece.order = order
    piece.save()
    return piece

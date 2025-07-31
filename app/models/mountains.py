from sqlmodel import Field, SQLModel


class GeoPoint(SQLModel, table=True):
    __tablename__ = 'geopoint'
    id: int | None = Field(default=None, primary_key=True)
    latitude: float = 0
    longitude: float = 0


class Ridge(SQLModel, table=True):
    """
    Ridge model
    """
    __tablename__ = 'ridge'
    id: int | None = Field(default=None, primary_key=True)
    slug: str | None = Field(default=None)
    name: str
    description: str | None = Field(default=None)
    # editor = models.ForeignKey(
    #    get_user_model(), on_delete=models.PROTECT, verbose_name=_("editor"), null=True)
    active: bool = Field(default=True)
    # changed = models.DateTimeField(
    #    _("created"), default=timezone.now, db_index=True)


# class GeoPoint(models.Model):
#     """
#     GeoPoint stores data related to point on Earth surface
#     """
#     latitude = models.DecimalField(
#         _("latitude"), default=0, decimal_places=6, max_digits=10)
#     longitude = models.DecimalField(
#         _("longitude"), default=0, decimal_places=6, max_digits=10)

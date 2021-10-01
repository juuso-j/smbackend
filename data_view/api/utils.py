from django.contrib.gis.gdal.error import GDALException

def transform_queryset(srid, queryset):
    try:
        for elem in queryset:

            print("HERE")
            elem.geometry.transform(srid)
    except GDALException:
        return False, queryset
    else:   
        return True, queryset

def transform_group_queryset(srid, queryset):
    try: 
      pass

    except GDALException:
        return False, queryset
    else:    
        return True, queryset
    

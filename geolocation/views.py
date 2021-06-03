from django.shortcuts import render
from django.views.generic import TemplateView
from shapely.geometry import Polygon, MultiPolygon, Point
import geopandas as gp
import folium

def convert_3D_2D(geometry):
    '''
    Takes a GeoSeries of 3D Multi/Polygons (has_z) and returns a list of 2D Multi/Polygons
    '''
    new_geo = []
    for p in geometry:
        if p.has_z:
            if p.geom_type == 'Polygon':
                lines = [xy[:2] for xy in list(p.exterior.coords)]
                new_p = Polygon(lines)
                new_geo.append(new_p)
            elif p.geom_type == 'MultiPolygon':
                new_multi_p = []
                for ap in p:
                    lines = [xy[:2] for xy in list(ap.exterior.coords)]
                    new_p = Polygon(lines)
                    new_multi_p.append(new_p)
                new_geo.append(MultiPolygon(new_multi_p))
    return new_geo
style1 = {'fillColor': 'ff1919', 'color': '#ff0000'}
style2 = {'fillColor': 'green', 'color': 'green'}
style3 = {'fillColor': '#9c5010', 'color': 'orange'}
style4 = {'fillColor': '#FFFF00', 'color': '#483D8B'}

def filter(geometry,ponto):
    for poly in geometry:
            if poly.geom_type == 'Polygon':
               if ponto.within(poly) or poly.within(ponto):
                    mask = poly  
                    return mask             
            elif poly.geom_type == 'MultiPolygon':
                for p in poly:
                    if ponto.within(p) or p.within(ponto):
                        mask = poly
                        return mask 
    return False

class IndexView(TemplateView):
    template_name ="geo/index.html"
    
    
    
def MapView(request):
    template_name ="geo/map.html"
    if request.method == "POST":
        lat = request.POST['latitude']
        long = request.POST['longitude']
         
        context={}
        m = folium.Map(location=[lat, long],width='100%', height=300, zoom_start=10)
        florestas = gp.read_file('data/florestas/Floresta_SireneJud_pocone.shp')
        desmatamento = gp.read_file('data/desmatamento/desmata.shp')   
        area_imovel = gp.read_file('data/car/AREA_IMOVEL.shp')       
        fogo = gp.read_file('data/queimadas/Focos_2020-06-01_2021-06-02.shp')   
        sigef = gp.read_file('data/sigef/Sigef_Brasil_MT.shp')
        
        florestas.geometry = convert_3D_2D(florestas.geometry)
        mask = []  
        ponto =Point(float(long),float(lat)) 
        mask_floresta = False 
        mask_desmata = False
        mask_area_imovel = False
        mask_sigef=False
        mask_floresta = filter(florestas['geometry'],ponto) 
        mask_desmata = filter(desmatamento['geometry'],ponto)
        mask_area_imovel = filter(area_imovel['geometry'],ponto)
        mask_sigef = filter(sigef['geometry'],ponto) 
        informacoes=""
        flores=""
        desmata=""
        rural=""
        sigef=""
        
        if mask_floresta:     
            geo_floresta =florestas[florestas['geometry']==mask_floresta]  
            latitudes = fogo['latitude']
            longitude = fogo['longitude']
            flores+='Nome: '+str(geo_floresta['nome'].values[0])+"\n"
            flores+='SireneJud: '+str(geo_floresta['SireneJud'].values[0])+"\n"
            context['flores']=flores
            for lat,long in zip(fogo['latitude'], fogo['longitude']):
                ponto =Point(float(long),float(lat))
                if geo_floresta['geometry'].contains(ponto).values[0]:
                    folium.Marker(location=[lat,long],popup="Queimada", icon=folium.Icon(color="red", icon="info-sign"),).add_to(m)
                           
        if mask_desmata:      
            geo_desmata = desmatamento[desmatamento['geometry']==mask_desmata] 
            desmata+='Cidade: '+str(geo_desmata['municipio'].values[0])+"\n"
            context['desmata']=desmata
            latitudes = fogo['latitude']
            longitude = fogo['longitude']
            for lat,long in zip(fogo['latitude'], fogo['longitude']):
                ponto =Point(float(long),float(lat))
                if geo_desmata['geometry'].contains(ponto).values[0]:
                    folium.Marker(location=[lat,long],popup="Queimada", icon=folium.Icon(color="red", icon="info-sign"),).add_to(m)
                  
        if mask_area_imovel:
            geo_area_imovel = area_imovel[area_imovel['geometry']==mask_area_imovel] 
            rural+='CAR: '+str(geo_area_imovel['COD_IMOVEL'].values[0])+"\n"
            context['rural']=rural
            latitudes = fogo['latitude']
            longitude = fogo['longitude']
            for lat,long in zip(fogo['latitude'], fogo['longitude']):
                ponto =Point(float(long),float(lat))
                if geo_area_imovel['geometry'].contains(ponto).values[0]:
                    folium.Marker(location=[lat,long],popup="Queimada", icon=folium.Icon(color="red", icon="info-sign"),).add_to(m)
        
        if mask_sigef:
            geo_sigef = sigef[sigef['geometry']==mask_area_imovel] 
            sigef = "Sigef "+str(geo_sigef['codigo_imo'].values[0])
            context['sigef']=sigef
            latitudes = fogo['latitude']
            longitude = fogo['longitude']
            for lat,long in zip(fogo['latitude'], fogo['longitude']):
                ponto =Point(float(long),float(lat))
                if geo_sigef['geometry'].contains(ponto).values[0]:
                    folium.Marker(location=[lat,long],popup="Queimada", icon=folium.Icon(color="red", icon="info-sign"),).add_to(m)
            
        if mask_floresta:    
            folium.GeoJson(data=geo_floresta["geometry"],style_function=lambda x:style2).add_to(m)
        if mask_area_imovel:    
            folium.GeoJson(data=geo_area_imovel["geometry"],style_function=lambda x:style3).add_to(m)
        if mask_desmata:    
            folium.GeoJson(data=geo_desmata["geometry"],style_function=lambda x:style4).add_to(m)
        if mask_sigef:    
           folium.GeoJson(data=geo_desmata["geometry"],style_function=lambda x:style1).add_to(m)
            
        
        mapa = m._repr_html_()  
        context['mapa']=mapa
        return render(request,template_name,context=context)
    return render(request,template_name)

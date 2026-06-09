// Abstracción para marcadores de mapa.
// Cuando se integre Leaflet, aquí se definirán las interfaces
// para crear y gestionar marcadores en el mapa.

export interface MapCoordinates {
  lat: number
  lng: number
}

export interface MapMarkerData {
  id: number | string
  position: MapCoordinates
  title: string
  description?: string
  icon?: string
  color?: string
}

// Ejemplo de uso futuro con Leaflet:
// import L from 'leaflet'
// export function createMarker(data: MapMarkerData): L.Marker {
//   return L.marker([data.position.lat, data.position.lng])
//     .bindPopup(`<b>${data.title}</b><p>${data.description || ''}</p>`)
// }

// var map = L.map('map').setView([36.3393, -97.9131], 10);

function rxNextTOMessage(chatSocket, runway) {

    chatSocket.addEventListener('message', function(e){

        let msg = JSON.parse(e.data)
        if(msg.type == 'nextTOMessage' && msg.runway == runway){
                let data = msg.data
                document.getElementById('nextTO--solo').checked = data.solo
                document.getElementById('nextTO--formationX2').checked = data.formationX2
                document.getElementById('nextTO--formationX4').checked = data.formationX4
        }
    })
}

function nextTOMessage(chatSocket, id, runway) {
    solo = document.getElementById('nextTO--solo').checked
    formationX2 = document.getElementById('nextTO--formationX2').checked
    formationX4 = document.getElementById('nextTO--formationX4').checked

    if(formationX2 == true && id == 'formationX4') {
        formationX4 = false
    }

    if(formationX4 == true && id == 'formationX2') {
        formationX2 = false
    }

    console.log(window.location.href)
    chatSocket.send(JSON.stringify({
      'type': 'nextTOMessage',
      'runway': runway,
      'data': {
        'solo': solo,
        'formationX2': formationX2,
        'formationX4': formationX4
      }
  }))
}



function load(chatSocket, csrf_token, lat, lon, FAAcode, runway, patternName) {

    // var map = L.map('map').setView([lat, lon], 10);

    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    L.marker([lat, lon]).addTo(map)
        .bindPopup(FAAcode)
        .openPopup();

    var MapAcft = {}
    var MapAcftNotUpdated = []
    var iconDict = {}

    for (let i = 0; i < displayedAcftTypes.length; i++) {

        let size = displayedAcftTypes[i].fields.iconSize
        
        //add normal icon
        iconDict[displayedAcftTypes[i].pk] = L.icon({
            iconUrl: "../../../media/AutoRecorder/" + displayedAcftTypes[i].fields.mapIconFile,
            iconSize:     [size, size], // size of the icon
            shadowSize:   [size, size], // size of the shadow
            iconAnchor:   [size/2, size/2], // point of the icon which will correspond to marker's location
            shadowAnchor: [0, 0],  // the same for the shadow
            popupAnchor:  [0, -1*size/2 + 10] // point from which the popup should open relative to the iconAnchor
        })

        //add translucent icon 
        iconDict[displayedAcftTypes[i].pk + "_translucent"] = L.icon({
            iconUrl: "../../../media/AutoRecorder/" + displayedAcftTypes[i].fields.lostSignalIconFile,
            iconSize:     [size, size], // size of the icon
            shadowSize:   [size, size], // size of the shadow
            iconAnchor:   [size/2, size/2], // point of the icon which will correspond to marker's location
            shadowAnchor: [0, 0],  // the same for the shadow
            popupAnchor:  [0, -1*size/2 + 10] // point from which the popup should open relative to the iconAnchor
        })

    }
    console.log(displayedAcftTypes)
    console.log(iconDict)
    
    chatSocket.addEventListener('message', function(e){
        let data = JSON.parse(e.data)


        
        if(data.type == 'rwyUpdate' && data.runway == runway){
            console.log(data.runway + " matched: " + runway)


            let rwyUpdate = JSON.parse(data.message)
            let rwyMeta = JSON.parse(data.meta)


            let Pattern = document.getElementById(' In Pattern')
            removeAllChildNodes(Pattern)
            let Taxiing = document.getElementById(' Taxiing')
            removeAllChildNodes(Taxiing)
            let OffStation = document.getElementById(' Off Station')
            removeAllChildNodes(OffStation)
            let LostSignal = document.getElementById(' Lost Signal')
            removeAllChildNodes(LostSignal)
            let numPattern = document.getElementById('num In Pattern')
            removeAllChildNodes(numPattern)
            let numTaxiing = document.getElementById('num Taxiing')
            removeAllChildNodes(numTaxiing)
            let numOffStation = document.getElementById('num Off Station')
            removeAllChildNodes(numOffStation)
            let numLostSignal = document.getElementById('num Lost Signal')
            removeAllChildNodes(numLostSignal)


            let dualLimit = document.getElementById(' Dual Aircraft Outside the Pattern Beyond Limits')
            removeAllChildNodes(dualLimit)
            let soloLimit = document.getElementById(' Solo Aircraft Outside the Pattern Beyond Limits')
            removeAllChildNodes(soloLimit)
            let solosOffStation = document.getElementById(' Solos Off Station')
            removeAllChildNodes(solosOffStation)
            let solosInPattern = document.getElementById(' Solos in the Pattern')
            removeAllChildNodes(solosInPattern)

            let numdualLimit = document.getElementById('num Dual Aircraft Outside the Pattern Beyond Limits')
            removeAllChildNodes(numdualLimit)
            let numsoloLimit = document.getElementById('num Solo Aircraft Outside the Pattern Beyond Limits')
            removeAllChildNodes(numsoloLimit)
            let numsolosOffStation = document.getElementById('num Solos Off Station')
            removeAllChildNodes(numsolosOffStation)
            let numsolosInPattern = document.getElementById('num Solos in the Pattern')
            removeAllChildNodes(numsolosInPattern)

            numdualLimit.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${rwyMeta.dualLimit.length}</span>
            `)
            
            numsoloLimit.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${rwyMeta.soloLimit.length}</span>
            `)
            
            numsolosOffStation.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${rwyMeta.solosOffStation.length}</span>
            `)
            
            numsolosInPattern.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${rwyMeta.solosInPattern.length}</span>
            `)

            //update the badge displaying the number of aircraft in each major state
            if(rwyMeta.In_Pattern < 8) { //blue background
                numPattern.insertAdjacentHTML('beforeend', `
                <span class="badge bg-primary rounded-pill">${rwyMeta.In_Pattern}</span>
                `)
            }
            else if (rwyMeta.In_Pattern >= 12) { //red background
                numPattern.insertAdjacentHTML('beforeend', `
                <span class="badge bg-danger rounded-pill">${rwyMeta.In_Pattern}</span>
                `)
            }
            else { //yellow background
                numPattern.insertAdjacentHTML('beforeend', `
                <span class="badge bg-warning rounded-pill">${rwyMeta.In_Pattern}</span>
                `)
            }

            numTaxiing.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${rwyMeta.Taxiing}</span>
            `)

            numOffStation.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${rwyMeta.Off_Station}</span>
            `)

            numLostSignal.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${rwyMeta.Lost_Signal}</span>
            `)

            for (let i = 0; i < rwyMeta.dualLimit.length; i++) {
                dualLimit.insertAdjacentHTML('beforeend', `
                <span class="badge text-bg-secondary">${rwyMeta.dualLimit[i]}</span>
                `
                )   
            }

            for (let i = 0; i < rwyMeta.soloLimit.length; i++) {
                soloLimit.insertAdjacentHTML('beforeend', `
                <span class="badge text-bg-danger">${rwyMeta.soloLimit[i]}</span>
                `
                )   
            }

            for (let i = 0; i < rwyMeta.solosOffStation.length; i++) {
                solosOffStation.insertAdjacentHTML('beforeend', `
                <span class="badge text-bg-warning">${rwyMeta.solosOffStation[i]}</span>
                `
                )   
            }

            for (let i = 0; i < rwyMeta.solosInPattern.length; i++) {
                solosInPattern.insertAdjacentHTML('beforeend', `
                <span class="badge text-bg-info">${rwyMeta.solosInPattern[i]}</span>
                `
                )   
            }

            MapAcftNotUpdated = {...MapAcft}
            console.log(MapAcftNotUpdated)
                            
            for (let i = 0; i < rwyUpdate.length; i++) {

                delete MapAcftNotUpdated[rwyUpdate[i].pk]
                let acftType = rwyUpdate[i].fields.aircraftType
                let formX2Checkmark = ""
                let formX4Checkmark = ""
                let soloCheckmark = ""
                if (rwyUpdate[i].fields.solo) {soloCheckmark = "checked"}
                if (rwyUpdate[i].fields.formationX2) {formX2Checkmark = "checked"}
                if (rwyUpdate[i].fields.formationX4) {formX4Checkmark = "checked"}
                
                if (rwyUpdate[i].fields.substate == patternName) {
                    if (!MapAcft[rwyUpdate[i].pk]) {
                        // If there is no marker with this id yet, instantiate a new one.;
                        MapAcft[rwyUpdate[i].pk] = L.marker([rwyUpdate[i].fields.latitude, rwyUpdate[i].fields.longitude], {rotationAngle: rwyUpdate[i].fields.track, icon: iconDict[acftType]}).addTo(map).bindPopup(rwyUpdate[i].fields.callSign);          
                      } else {
                        // If there is already a marker with this id, simply modify its position.
                        MapAcft[rwyUpdate[i].pk].setLatLng([rwyUpdate[i].fields.latitude, rwyUpdate[i].fields.longitude]).setRotationAngle(rwyUpdate[i].fields.track).setPopupContent(rwyUpdate[i].fields.callSign);
                        MapAcft[rwyUpdate[i].pk].setIcon(iconDict[acftType]);
                      }

                    Pattern.insertAdjacentHTML('beforeend',       
                            `<tr>
                            <th scope="row"><a href="../../dashboard/edit/${rwyUpdate[i].pk}" class="btn btn-primary btn-sm">edit</a></th>
                            <td>${rwyUpdate[i].pk.slice(-3)}</td>
                            <td>${rwyUpdate[i].fields.callSign}</td>
                            <td>${rwyUpdate[i].fields.alt_baro}</td>
                            <td>${rwyUpdate[i].fields.groundSpeed}</td>
                            <td>${String(rwyUpdate[i].fields.takeoffTime).slice(11, -8).concat(String(rwyUpdate[i].fields.takeoffTime).slice(23))}</td>
                            <td>${String(rwyUpdate[i].fields.landTime).slice(11, -8).concat(String(rwyUpdate[i].fields.landTime).slice(23))}</td>

                            <td style="padding-top: 0px; padding-bottom: 0px; white-space: nowrap;">
                                <table><tr><td>
                                    <form method="POST" action="${window.location.href}/formX2/${rwyUpdate[i].pk}" class="form-group">    
                                        <input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
                                        <input onChange="this.form.submit()" class="form-check-input" type="checkbox" value="" id="flexCheck${rwyUpdate[i].pk}" ${formX2Checkmark}>  
                                        <label class="form-check-label" for="flexCheck${rwyUpdate[i].pk}">2-Ship</label>     
                                    </form>
                                </td></tr>
                                <tr><td>
                                    <form method="POST" action="${window.location.href}/formX4/${rwyUpdate[i].pk}" class="form-group">
                                        <input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
                                        <input onChange="this.form.submit()" class="form-check-input" type="checkbox" value="" id="flexCheck${rwyUpdate[i].pk}" ${formX4Checkmark}>  
                                        <label class="form-check-label" for="flexCheck${rwyUpdate[i].pk}">4-Ship</label>
                                    </form>
                                </td></tr></table>
                            </td>

                            <td>
                            <form method="POST" action="${window.location.href}/solo/${rwyUpdate[i].pk}" class="form-group">
                                <input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
                                <input onChange="this.form.submit()" class="form-check-input" type="checkbox" value="" id="flexCheck${rwyUpdate[i].pk}" ${soloCheckmark}>  
                                <label class="form-check-label" for="flexCheck${rwyUpdate[i].pk}">Solo</label>
                            </form>
                            </td>

                            <td><center><a href="../../dashboard/355/${rwyUpdate[i].pk}" class="btn btn-primary btn-sm btn-danger">355</a></center></td>
                            </tr>`
                            )

                }

                // Display aircraft in other patterns
                if (rwyUpdate[i].fields.state == "in pattern" && rwyUpdate[i].fields.substate != patternName) {
                    if (!MapAcft[rwyUpdate[i].pk]) {
                        // If there is no marker with this id yet, instantiate a new one.;
                        MapAcft[rwyUpdate[i].pk] = L.marker([rwyUpdate[i].fields.latitude, rwyUpdate[i].fields.longitude], {rotationAngle: rwyUpdate[i].fields.track, icon: iconDict[acftType]}).addTo(map).bindPopup(rwyUpdate[i].fields.callSign);          
                      } else {
                        // If there is already a marker with this id, simply modify its position.
                        MapAcft[rwyUpdate[i].pk].setLatLng([rwyUpdate[i].fields.latitude, rwyUpdate[i].fields.longitude]).setRotationAngle(rwyUpdate[i].fields.track).setPopupContent(rwyUpdate[i].fields.callSign);
                        MapAcft[rwyUpdate[i].pk].setIcon(iconDict[acftType]);
                      }
                }

                if (rwyUpdate[i].fields.state == "taxiing") {
                    if (!MapAcft[rwyUpdate[i].pk]) {
                        // If there is no marker with this id yet, instantiate a new one.;
                        MapAcft[rwyUpdate[i].pk] = L.marker([rwyUpdate[i].fields.latitude, rwyUpdate[i].fields.longitude], {rotationAngle: rwyUpdate[i].fields.track, icon: iconDict[acftType + "_translucent"]}).addTo(map).bindPopup(rwyUpdate[i].fields.callSign);          
                      } else {
                        // If there is already a marker with this id, simply modify its position.
                        MapAcft[rwyUpdate[i].pk].setLatLng([rwyUpdate[i].fields.latitude, rwyUpdate[i].fields.longitude]).setRotationAngle(rwyUpdate[i].fields.track).setPopupContent(rwyUpdate[i].fields.callSign);
                        MapAcft[rwyUpdate[i].pk].setIcon(iconDict[acftType + "_translucent"]);
                      }

                    Taxiing.insertAdjacentHTML('beforeend',       
                    `<tr>
                    <th scope="row"><a href="../../dashboard/edit/${rwyUpdate[i].pk}" class="btn btn-primary btn-sm">edit</a></th>
                    <td>${rwyUpdate[i].pk.slice(-3)}</td>
                    <td>${rwyUpdate[i].fields.callSign}</td>
                    <td>${rwyUpdate[i].fields.alt_baro}</td>
                    <td>${rwyUpdate[i].fields.groundSpeed}</td>
                    <td>${String(rwyUpdate[i].fields.takeoffTime).slice(11, -8).concat(String(rwyUpdate[i].fields.takeoffTime).slice(23))}</td>
                    <td>${String(rwyUpdate[i].fields.landTime).slice(11, -8).concat(String(rwyUpdate[i].fields.landTime).slice(23))}</td>

                    <td style="padding-top: 0px; padding-bottom: 0px; white-space: nowrap;">
                        <table><tr><td>
                            <form method="POST" action="${window.location.href}/formX2/${rwyUpdate[i].pk}" class="form-group">    
                                <input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
                                <input onChange="this.form.submit()" class="form-check-input" type="checkbox" value="" id="flexCheck${rwyUpdate[i].pk}" ${formX2Checkmark}>  
                                <label class="form-check-label" for="flexCheck${rwyUpdate[i].pk}">2-Ship</label>     
                            </form>
                        </td></tr>
                        <tr><td>
                            <form method="POST" action="${window.location.href}/formX4/${rwyUpdate[i].pk}" class="form-group">
                                <input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
                                <input onChange="this.form.submit()" class="form-check-input" type="checkbox" value="" id="flexCheck${rwyUpdate[i].pk}" ${formX4Checkmark}>  
                                <label class="form-check-label" for="flexCheck${rwyUpdate[i].pk}">4-Ship</label>
                            </form>
                        </td></tr></table>
                    </td>

                    <td>
                    <form method="POST" action="${window.location.href}/solo/${rwyUpdate[i].pk}" class="form-group">
                        <input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
                        <input onChange="this.form.submit()" class="form-check-input" type="checkbox" value="" id="flexCheck${rwyUpdate[i].pk}" ${soloCheckmark}>  
                        <label class="form-check-label" for="flexCheck${rwyUpdate[i].pk}">Solo</label>
                    </form>
                    </td>

                    <td><center><a href="../../dashboard/355/${rwyUpdate[i].pk}" class="btn btn-primary btn-sm btn-danger">355</a></center></td>
                    </tr>`
                    )
                }
                if (rwyUpdate[i].fields.state == "off station") {
                    if (!MapAcft[rwyUpdate[i].pk]) {
                        // If there is no marker with this id yet, instantiate a new one.;
                        MapAcft[rwyUpdate[i].pk] = L.marker([rwyUpdate[i].fields.latitude, rwyUpdate[i].fields.longitude], {rotationAngle: rwyUpdate[i].fields.track, icon: iconDict[acftType]}).addTo(map).bindPopup(rwyUpdate[i].fields.callSign);          
                      } else {
                        // If there is already a marker with this id, simply modify its position.
                        MapAcft[rwyUpdate[i].pk].setLatLng([rwyUpdate[i].fields.latitude, rwyUpdate[i].fields.longitude]).setRotationAngle(rwyUpdate[i].fields.track).setPopupContent(rwyUpdate[i].fields.callSign);
                        MapAcft[rwyUpdate[i].pk].setIcon(iconDict[acftType]);
                      }

                    OffStation.insertAdjacentHTML('beforeend',       
                    `<tr>
                    <th scope="row"><a href="../../dashboard/edit/${rwyUpdate[i].pk}" class="btn btn-primary btn-sm">edit</a></th>
                    <td>${rwyUpdate[i].pk.slice(-3)}</td>
                    <td>${rwyUpdate[i].fields.callSign}</td>
                    <td>${rwyUpdate[i].fields.alt_baro}</td>
                    <td>${rwyUpdate[i].fields.groundSpeed}</td>
                    <td>${String(rwyUpdate[i].fields.takeoffTime).slice(11, -8).concat(String(rwyUpdate[i].fields.takeoffTime).slice(23))}</td>
                    <td>${String(rwyUpdate[i].fields.landTime).slice(11, -8).concat(String(rwyUpdate[i].fields.landTime).slice(23))}</td>

                    <td style="padding-top: 0px; padding-bottom: 0px; white-space: nowrap;">
                        <table><tr><td>
                            <form method="POST" action="${window.location.href}/formX2/${rwyUpdate[i].pk}" class="form-group">    
                                <input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
                                <input onChange="this.form.submit()" class="form-check-input" type="checkbox" value="" id="flexCheck${rwyUpdate[i].pk}" ${formX2Checkmark}>  
                                <label class="form-check-label" for="flexCheck${rwyUpdate[i].pk}">2-Ship</label>     
                            </form>
                        </td></tr>
                        <tr><td>
                            <form method="POST" action="${window.location.href}/formX4/${rwyUpdate[i].pk}" class="form-group">
                                <input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
                                <input onChange="this.form.submit()" class="form-check-input" type="checkbox" value="" id="flexCheck${rwyUpdate[i].pk}" ${formX4Checkmark}>  
                                <label class="form-check-label" for="flexCheck${rwyUpdate[i].pk}">4-Ship</label>
                            </form>
                        </td></tr></table>
                    </td>

                    <td>
                    <form method="POST" action="${window.location.href}/solo/${rwyUpdate[i].pk}" class="form-group">
                        <input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
                        <input onChange="this.form.submit()" class="form-check-input" type="checkbox" value="" id="flexCheck${rwyUpdate[i].pk}" ${soloCheckmark}>  
                        <label class="form-check-label" for="flexCheck${rwyUpdate[i].pk}">Solo</label>
                    </form>
                    </td>

                    <td><center><a href="../../dashboard/355/${rwyUpdate[i].pk}" class="btn btn-primary btn-sm btn-danger">355</a></center></td>
                    </tr>`
                    )
                }
                if (rwyUpdate[i].fields.state == "lost signal") {
                    if (!MapAcft[rwyUpdate[i].pk]) {
                        // If there is no marker with this id yet, instantiate a new one.;
                        MapAcft[rwyUpdate[i].pk] = L.marker([rwyUpdate[i].fields.latitude, rwyUpdate[i].fields.longitude], {rotationAngle: rwyUpdate[i].fields.track, icon: iconDict[acftType + "_translucent"]}).addTo(map).bindPopup(rwyUpdate[i].fields.callSign);          
                      } else {
                        // If there is already a marker with this id, simply modify its position.
                        MapAcft[rwyUpdate[i].pk].setLatLng([rwyUpdate[i].fields.latitude, rwyUpdate[i].fields.longitude]).setRotationAngle(rwyUpdate[i].fields.track).setPopupContent(rwyUpdate[i].fields.callSign);
                        MapAcft[rwyUpdate[i].pk].setIcon(iconDict[acftType + "_translucent"]);
                      }

                    LostSignal.insertAdjacentHTML('beforeend',       
                    `<tr>
                    <th scope="row"><a href="../../dashboard/edit/${rwyUpdate[i].pk}" class="btn btn-primary btn-sm">edit</a></th>
                    <td>${rwyUpdate[i].pk.slice(-3)}</td>
                    <td>${rwyUpdate[i].fields.callSign}</td>
                    <td>${rwyUpdate[i].fields.alt_baro}</td>
                    <td>${rwyUpdate[i].fields.groundSpeed}</td>
                    <td>${String(rwyUpdate[i].fields.takeoffTime).slice(11, -8).concat(String(rwyUpdate[i].fields.takeoffTime).slice(23))}</td>
                    <td>${String(rwyUpdate[i].fields.landTime).slice(11, -8).concat(String(rwyUpdate[i].fields.landTime).slice(23))}</td>

                    <td style="padding-top: 0px; padding-bottom: 0px; white-space: nowrap;">
                        <table><tr><td>
                            <form method="POST" action="${window.location.href}/formX2/${rwyUpdate[i].pk}" class="form-group">    
                                <input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
                                <input onChange="this.form.submit()" class="form-check-input" type="checkbox" value="" id="flexCheck${rwyUpdate[i].pk}" ${formX2Checkmark}>  
                                <label class="form-check-label" for="flexCheck${rwyUpdate[i].pk}">2-Ship</label>     
                            </form>
                        </td></tr>
                        <tr><td>
                            <form method="POST" action="${window.location.href}/formX4/${rwyUpdate[i].pk}" class="form-group">
                                <input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
                                <input onChange="this.form.submit()" class="form-check-input" type="checkbox" value="" id="flexCheck${rwyUpdate[i].pk}" ${formX4Checkmark}>  
                                <label class="form-check-label" for="flexCheck${rwyUpdate[i].pk}">4-Ship</label>
                            </form>
                        </td></tr></table>
                    </td>

                    <td>
                    <form method="POST" action="${window.location.href}/solo/${rwyUpdate[i].pk}" class="form-group">
                        <input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
                        <input onChange="this.form.submit()" class="form-check-input" type="checkbox" value="" id="flexCheck${rwyUpdate[i].pk}" ${soloCheckmark}>  
                        <label class="form-check-label" for="flexCheck${rwyUpdate[i].pk}">Solo</label>
                    </form>
                    </td>

                    <td><center><a href="../../dashboard/355/${rwyUpdate[i].pk}" class="btn btn-primary btn-sm btn-danger">355</a></center></td>
                    </tr>`
                    )
                }
            }
                        //remove all aircraft on the map that were not in the update message
            for (const[tailNumber, data] of Object.entries(MapAcftNotUpdated)) {
                map.removeLayer(MapAcft[tailNumber])
                delete MapAcft[tailNumber]
            }

        }
    }
    )
}

// function removeAllChildNodes(parent) {
// while (parent.firstChild) {
//     parent.removeChild(parent.firstChild);
// }
// }
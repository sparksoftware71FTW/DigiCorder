function loadKEND35R(chatSocket) {

    chatSocket.addEventListener('message', function(e){
        let data = JSON.parse(e.data)

        if(data.type == 't6Update'){

            let t6Update = JSON.parse(data.message)
            let t6Meta = JSON.parse(data.meta)
            console.log("HELLLOOOOOOOOOOOOOO")

            let KEND35RPattern = document.getElementById('KEND35R In Pattern')
            removeAllChildNodes(KEND35RPattern)
            let KEND35RTaxiing = document.getElementById('KEND35R Taxiing')
            removeAllChildNodes(KEND35RTaxiing)
            let KEND35ROffStation = document.getElementById('KEND35R Off Station')
            removeAllChildNodes(KEND35ROffStation)
            let KEND35RLostSignal = document.getElementById('KEND35R Lost Signal')
            removeAllChildNodes(KEND35RLostSignal)
            let numKEND35RPattern = document.getElementById('numKEND35R In Pattern')
            removeAllChildNodes(numKEND35RPattern)
            let numKEND35RTaxiing = document.getElementById('numKEND35R Taxiing')
            removeAllChildNodes(numKEND35RTaxiing)
            let numKEND35ROffStation = document.getElementById('numKEND35R Off Station')
            removeAllChildNodes(numKEND35ROffStation)
            let numKEND35RLostSignal = document.getElementById('numKEND35R Lost Signal')
            removeAllChildNodes(numKEND35RLostSignal)


            let KEND35Rdual145 = document.getElementById('KEND35R Dual Aircraft Outside the Pattern > 1+45')
            removeAllChildNodes(KEND35Rdual145)
            let KEND35Rsolo120 = document.getElementById('KEND35R Solo Aircraft Outside the Pattern > 1+20')
            removeAllChildNodes(KEND35Rsolo120)
            let KEND35RsolosOffStation = document.getElementById('KEND35R Solos Off Station')
            removeAllChildNodes(KEND35RsolosOffStation)
            let KEND35RsolosInPattern = document.getElementById('KEND35R Solos in the Pattern')
            removeAllChildNodes(KEND35RsolosInPattern)

            let numKEND35Rdual145 = document.getElementById('numKEND35R Dual Aircraft Outside the Pattern > 1+45')
            removeAllChildNodes(numKEND35Rdual145)
            let numKEND35Rsolo120 = document.getElementById('numKEND35R Solo Aircraft Outside the Pattern > 1+20')
            removeAllChildNodes(numKEND35Rsolo120)
            let numKEND35RsolosOffStation = document.getElementById('numKEND35R Solos Off Station')
            removeAllChildNodes(numKEND35RsolosOffStation)
            let numKEND35RsolosInPattern = document.getElementById('numKEND35R Solos in the Pattern')
            removeAllChildNodes(numKEND35RsolosInPattern)

            numKEND35Rdual145.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t6Meta.dual145.length}</span>
            `)
            
            numKEND35Rsolo120.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t6Meta.solo120.length}</span>
            `)
            
            numKEND35RsolosOffStation.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t6Meta.solosOffStation.length}</span>
            `)
            
            numKEND35RsolosInPattern.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t6Meta.solosInPattern.length}</span>
            `)

            //update the badge displaying the number of aircraft in each major state
            if(t6Meta.In_Pattern < 8) { //blue background
                numKEND35RPattern.insertAdjacentHTML('beforeend', `
                <span class="badge bg-primary rounded-pill">${t6Meta.In_Pattern}</span>
                `)
            }
            else if (t6Meta.In_Pattern >= 12) { //red background
                numKEND35RPattern.insertAdjacentHTML('beforeend', `
                <span class="badge bg-danger rounded-pill">${t6Meta.In_Pattern}</span>
                `)
            }
            else { //yellow background
                numKEND35RPattern.insertAdjacentHTML('beforeend', `
                <span class="badge bg-warning rounded-pill">${t6Meta.In_Pattern}</span>
                `)
            }

            numKEND35RTaxiing.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t6Meta.Taxiing}</span>
            `)

            numKEND35ROffStation.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t6Meta.Off_Station}</span>
            `)

            numKEND35RLostSignal.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t6Meta.Lost_Signal}</span>
            `)

            for (let i = 0; i < t6Meta.dual145.length; i++) {
                KEND35Rdual145.insertAdjacentHTML('beforeend', `
                <span class="badge text-bg-secondary">${t6Meta.dual145[i]}</span>
                `
                )   
            }

            for (let i = 0; i < t6Meta.solo120.length; i++) {
                KEND35Rsolo120.insertAdjacentHTML('beforeend', `
                <span class="badge text-bg-danger">${t6Meta.solo120[i]}</span>
                `
                )   
            }

            for (let i = 0; i < t6Meta.solosOffStation.length; i++) {
                KEND35RsolosOffStation.insertAdjacentHTML('beforeend', `
                <span class="badge text-bg-warning">${t6Meta.solosOffStation[i]}</span>
                `
                )   
            }

            for (let i = 0; i < t6Meta.solosInPattern.length; i++) {
                KEND35RsolosInPattern.insertAdjacentHTML('beforeend', `
                <span class="badge text-bg-info">${t6Meta.solosInPattern[i]}</span>
                `
                )   
            }

            
            for (let i = 0; i < t6Update.length; i++) {

                if (t6Update[i].fields.state == "in pattern") {
                    KEND35RPattern.insertAdjacentHTML('beforeend',       
                            `<tr>
                            <th scope="row"><a href="#" class="btn btn-primary btn-sm">edit</a></th>
                            <td>${t6Update[i].pk}</td>
                            <td>${t6Update[i].fields.callSign}</td>
                            <td>${t6Update[i].fields.alt_baro}</td>
                            <td>${t6Update[i].fields.groundSpeed}</td>
                            <td>${t6Update[i].fields.takeoffTime}</td>
                            <td>${t6Update[i].fields.landTime}</td>

                            <td>  
                                <input class="form-check-input" type="checkbox" value="" id="flexCheckDefault">
                                <label class="form-check-label" for="flexCheckDefault">Form Solo</label></td>
                            <td><a href="#" class="btn btn-primary btn-sm btn-danger">355</a></td>
                            </tr>`
                            )
                }
                if (t6Update[i].fields.state == "taxiing") {
                    KEND35RTaxiing.insertAdjacentHTML('beforeend',       
                            `<tr>
                            <th scope="row"><a href="#" class="btn btn-primary btn-sm">edit</a></th>
                            <td>${t6Update[i].pk}</td>
                            <td>${t6Update[i].fields.callSign}</td>
                            <td>${t6Update[i].fields.alt_baro}</td>
                            <td>${t6Update[i].fields.groundSpeed}</td>
                            <td>${t6Update[i].fields.takeoffTime}</td>
                            <td>${t6Update[i].fields.landTime}</td>

                            <td>  
                                <input class="form-check-input" type="checkbox" value="" id="flexCheckDefault">
                                <label class="form-check-label" for="flexCheckDefault">Form Solo</label></td>
                            <td><a href="#" class="btn btn-primary btn-sm btn-danger">355</a></td>
                            </tr>`
                            )
                }
                if (t6Update[i].fields.state == "off station") {
                    KEND35ROffStation.insertAdjacentHTML('beforeend',       
                            `<tr>
                            <th scope="row"><a href="#" class="btn btn-primary btn-sm">edit</a></th>
                            <td>${t6Update[i].pk}</td>
                            <td>${t6Update[i].fields.callSign}</td>
                            <td>${t6Update[i].fields.alt_baro}</td>
                            <td>${t6Update[i].fields.groundSpeed}</td>
                            <td>${t6Update[i].fields.takeoffTime}</td>
                            <td>${t6Update[i].fields.landTime}</td>

                            <td>  
                                <input class="form-check-input" type="checkbox" value="" id="flexCheckDefault">
                                <label class="form-check-label" for="flexCheckDefault">Form Solo</label></td>
                            <td><a href="#" class="btn btn-primary btn-sm btn-danger">355</a></td>
                            </tr>`
                            )
                }
                if (t6Update[i].fields.state == "lost signal") {
                    KEND35RLostSignal.insertAdjacentHTML('beforeend',       
                            `<tr>
                            <th scope="row"><a href="#" class="btn btn-primary btn-sm">edit</a></th>
                            <td>${t6Update[i].pk}</td>
                            <td>${t6Update[i].fields.callSign}</td>
                            <td>${t6Update[i].fields.alt_baro}</td>
                            <td>${t6Update[i].fields.groundSpeed}</td>
                            <td>${t6Update[i].fields.takeoffTime}</td>
                            <td>${t6Update[i].fields.landTime}</td>

                            <td>  
                                <input class="form-check-input" type="checkbox" value="" id="flexCheckDefault">
                                <label class="form-check-label" for="flexCheckDefault">Form Solo</label></td>
                            <td><a href="#" class="btn btn-primary btn-sm btn-danger">355</a></td>
                            </tr>`
                            )
                }
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
function loadKEND35L(chatSocket) {

    chatSocket.addEventListener('message', function(e){
        let data = JSON.parse(e.data)

        if(data.type == 't38Update'){

            let t38Update = JSON.parse(data.message)
            let t38Meta = JSON.parse(data.meta)
            console.log("HELLLOOOOOOOOOOOOOO")


            let KEND35LPattern = document.getElementById('KEND35L In Pattern')
            removeAllChildNodes(KEND35LPattern)
            let KEND35LTaxiing = document.getElementById('KEND35L Taxiing')
            removeAllChildNodes(KEND35LTaxiing)
            let KEND35LOffStation = document.getElementById('KEND35L Off Station')
            removeAllChildNodes(KEND35LOffStation)
            let KEND35LLostSignal = document.getElementById('KEND35L Lost Signal')
            removeAllChildNodes(KEND35LLostSignal)
            let numKEND35LPattern = document.getElementById('numKEND35L In Pattern')
            removeAllChildNodes(numKEND35LPattern)
            let numKEND35LTaxiing = document.getElementById('numKEND35L Taxiing')
            removeAllChildNodes(numKEND35LTaxiing)
            let numKEND35LOffStation = document.getElementById('numKEND35L Off Station')
            removeAllChildNodes(numKEND35LOffStation)
            let numKEND35LLostSignal = document.getElementById('numKEND35L Lost Signal')
            removeAllChildNodes(numKEND35LLostSignal)


            let KEND35Ldual120 = document.getElementById('KEND35L Dual Aircraft Outside the Pattern > 1+20')
            removeAllChildNodes(KEND35Ldual120)
            let KEND35Lsolo100 = document.getElementById('KEND35L Solo Aircraft Outside the Pattern > 1+00')
            removeAllChildNodes(KEND35Lsolo100)
            let KEND35LsolosOffStation = document.getElementById('KEND35L Solos Off Station')
            removeAllChildNodes(KEND35LsolosOffStation)
            let KEND35LsolosInPattern = document.getElementById('KEND35L Solos in the Pattern')
            removeAllChildNodes(KEND35LsolosInPattern)

            let numKEND35Ldual120 = document.getElementById('numKEND35L Dual Aircraft Outside the Pattern > 1+20')
            removeAllChildNodes(numKEND35Ldual120)
            let numKEND35Lsolo100 = document.getElementById('numKEND35L Solo Aircraft Outside the Pattern > 1+00')
            removeAllChildNodes(numKEND35Lsolo100)
            let numKEND35LsolosOffStation = document.getElementById('numKEND35L Solos Off Station')
            removeAllChildNodes(numKEND35LsolosOffStation)
            let numKEND35LsolosInPattern = document.getElementById('numKEND35L Solos in the Pattern')
            removeAllChildNodes(numKEND35LsolosInPattern)

            numKEND35Ldual120.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t38Meta.dual120.length}</span>
            `)
            
            numKEND35Lsolo100.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t38Meta.solo100.length}</span>
            `)
            
            numKEND35LsolosOffStation.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t38Meta.solosOffStation.length}</span>
            `)
            
            numKEND35LsolosInPattern.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t38Meta.solosInPattern.length}</span>
            `)

            //update the badge displaying the number of aircraft in each major state
            if(t38Meta.In_Pattern < 8) { //blue background
                numKEND35LPattern.insertAdjacentHTML('beforeend', `
                <span class="badge bg-primary rounded-pill">${t38Meta.In_Pattern}</span>
                `)
            }
            else if (t38Meta.In_Pattern >= 12) { //red background
                numKEND35LPattern.insertAdjacentHTML('beforeend', `
                <span class="badge bg-danger rounded-pill">${t38Meta.In_Pattern}</span>
                `)
            }
            else { //yellow background
                numKEND35LPattern.insertAdjacentHTML('beforeend', `
                <span class="badge bg-warning rounded-pill">${t38Meta.In_Pattern}</span>
                `)
            }

            numKEND35LTaxiing.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t38Meta.Taxiing}</span>
            `)

            numKEND35LOffStation.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t38Meta.Off_Station}</span>
            `)

            numKEND35LLostSignal.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t38Meta.Lost_Signal}</span>
            `)

            for (let i = 0; i < t38Meta.dual120.length; i++) {
                KEND35Ldual120.insertAdjacentHTML('beforeend', `
                <span class="badge text-bg-secondary">${t38Meta.dual120[i]}</span>
                `
                )   
            }

            for (let i = 0; i < t38Meta.solo100.length; i++) {
                KEND35Lsolo100.insertAdjacentHTML('beforeend', `
                <span class="badge text-bg-danger">${t38Meta.solo100[i]}</span>
                `
                )   
            }

            for (let i = 0; i < t38Meta.solosOffStation.length; i++) {
                KEND35LsolosOffStation.insertAdjacentHTML('beforeend', `
                <span class="badge text-bg-warning">${t38Meta.solosOffStation[i]}</span>
                `
                )   
            }

            for (let i = 0; i < t38Meta.solosInPattern.length; i++) {
                KEND35LsolosInPattern.insertAdjacentHTML('beforeend', `
                <span class="badge text-bg-info">${t38Meta.solosInPattern[i]}</span>
                `
                )   
            }

            
            for (let i = 0; i < t38Update.length; i++) {

                if (t38Update[i].fields.state == "in pattern") {
                    KEND35LPattern.insertAdjacentHTML('beforeend',       
                            `<tr>
                            <th scope="row"><a href="dashboard/edit/${t38Update[i].pk}" class="btn btn-primary btn-sm">edit</a></th>
                            <td>${t38Update[i].pk}</td>
                            <td>${t38Update[i].fields.callSign}</td>
                            <td>${t38Update[i].fields.alt_baro}</td>
                            <td>${t38Update[i].fields.groundSpeed}</td>
                            <td>${t38Update[i].fields.takeoffTime}</td>
                            <td>${t38Update[i].fields.landTime}</td>

                            <td>  
                                <input class="form-check-input" type="checkbox" value="" id="flexCheckDefault">
                                <label class="form-check-label" for="flexCheckDefault">Form Solo</label></td>
                                <td><a href="dashboard/355/${t38Update[i].pk}" class="btn btn-primary btn-sm btn-danger">355</a></td>
                            </tr>`
                            )
                }
                if (t38Update[i].fields.state == "taxiing") {
                    KEND35LTaxiing.insertAdjacentHTML('beforeend',       
                            `<tr>
                            <th scope="row"><a href="dashboard/edit/${t38Update[i].pk}" class="btn btn-primary btn-sm">edit</a></th>
                            <td>${t38Update[i].pk}</td>
                            <td>${t38Update[i].fields.callSign}</td>
                            <td>${t38Update[i].fields.alt_baro}</td>
                            <td>${t38Update[i].fields.groundSpeed}</td>
                            <td>${t38Update[i].fields.takeoffTime}</td>
                            <td>${t38Update[i].fields.landTime}</td>

                            <td>  
                                <input class="form-check-input" type="checkbox" value="" id="flexCheckDefault">
                                <label class="form-check-label" for="flexCheckDefault">Form Solo</label></td>
                                <td><a href="dashboard/355/${t38Update[i].pk}" class="btn btn-primary btn-sm btn-danger">355</a></td>
                            </tr>`
                            )
                }
                if (t38Update[i].fields.state == "off station") {
                    KEND35LOffStation.insertAdjacentHTML('beforeend',       
                            `<tr>
                            <th scope="row"><a href="dashboard/edit/${t38Update[i].pk}" class="btn btn-primary btn-sm">edit</a></th>
                            <td>${t38Update[i].pk}</td>
                            <td>${t38Update[i].fields.callSign}</td>
                            <td>${t38Update[i].fields.alt_baro}</td>
                            <td>${t38Update[i].fields.groundSpeed}</td>
                            <td>${t38Update[i].fields.takeoffTime}</td>
                            <td>${t38Update[i].fields.landTime}</td>

                            <td>  
                                <input class="form-check-input" type="checkbox" value="" id="flexCheckDefault">
                                <label class="form-check-label" for="flexCheckDefault">Form Solo</label></td>
                                <td><a href="dashboard/355/${t38Update[i].pk}" class="btn btn-primary btn-sm btn-danger">355</a></td>
                            </tr>`
                            )
                }
                if (t38Update[i].fields.state == "lost signal") {
                    KEND35LLostSignal.insertAdjacentHTML('beforeend',       
                            `<tr>
                            <th scope="row"><a href="dashboard/edit/${t38Update[i].pk}" class="btn btn-primary btn-sm">edit</a></th>
                            <td>${t38Update[i].pk}</td>
                            <td>${t38Update[i].fields.callSign}</td>
                            <td>${t38Update[i].fields.alt_baro}</td>
                            <td>${t38Update[i].fields.groundSpeed}</td>
                            <td>${t38Update[i].fields.takeoffTime}</td>
                            <td>${t38Update[i].fields.landTime}</td>

                            <td>  
                                <input class="form-check-input" type="checkbox" value="" id="flexCheckDefault">
                                <label class="form-check-label" for="flexCheckDefault">Form Solo</label></td>
                                <td><a href="dashboard/355/${t38Update[i].pk}" class="btn btn-primary btn-sm btn-danger">355</a></td>
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
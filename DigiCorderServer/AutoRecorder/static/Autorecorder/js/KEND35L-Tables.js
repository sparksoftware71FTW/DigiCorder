function loadKEND35L(chatSocket) {

    chatSocket.addEventListener('message', function(e){
        let data = JSON.parse(e.data)

        if(data.type == 't38Update'){

            let t38Update = JSON.parse(data.message)

            let KEND35LPattern = document.getElementById('KEND35L In Pattern')
            removeAllChildNodes(KEND35LPattern)
            let KEND35LTaxiing = document.getElementById('KEND35L Taxiing')
            removeAllChildNodes(KEND35LTaxiing)
            let KEND35LOffStation = document.getElementById('KEND35L Off Station')
            removeAllChildNodes(KEND35LOffStation)
            let KEND35LLostSignal = document.getElementById('KEND35L Lost Signal')
            removeAllChildNodes(KEND35LLostSignal)



            for (let i = 0; i < t38Update.length; i++) {

                if (t38Update[i].fields.state == "in pattern") {
                    KEND35LPattern.insertAdjacentHTML('beforeend',       
                            `<tr>
                            <th scope="row"><a href="#" class="btn btn-primary btn-sm">edit</a></th>
                            <td>${t38Update[i].pk}</td>
                            <td>${t38Update[i].fields.callSign}</td>
                            <td>${t38Update[i].fields.alt_baro}</td>
                            <td>${t38Update[i].fields.groundSpeed}</td>
                            <td>${t38Update[i].fields.takeoffTime}</td>
                            <td>${t38Update[i].fields.landTime}</td>

                            <td>  
                                <input class="form-check-input" type="checkbox" value="" id="flexCheckDefault">
                                <label class="form-check-label" for="flexCheckDefault">Form Solo</label></td>
                            <td><a href="#" class="btn btn-primary btn-sm btn-danger">355</a></td>
                            </tr>`
                            )
                }
                if (t38Update[i].fields.state == "taxiing") {
                    KEND35LTaxiing.insertAdjacentHTML('beforeend',       
                            `<tr>
                            <th scope="row"><a href="#" class="btn btn-primary btn-sm">edit</a></th>
                            <td>${t38Update[i].pk}</td>
                            <td>${t38Update[i].fields.callSign}</td>
                            <td>${t38Update[i].fields.alt_baro}</td>
                            <td>${t38Update[i].fields.groundSpeed}</td>
                            <td>${t38Update[i].fields.takeoffTime}</td>
                            <td>${t38Update[i].fields.landTime}</td>

                            <td>  
                                <input class="form-check-input" type="checkbox" value="" id="flexCheckDefault">
                                <label class="form-check-label" for="flexCheckDefault">Form Solo</label></td>
                            <td><a href="#" class="btn btn-primary btn-sm btn-danger">355</a></td>
                            </tr>`
                            )
                }
                if (t38Update[i].fields.state == "off station") {
                    KEND35LOffStation.insertAdjacentHTML('beforeend',       
                            `<tr>
                            <th scope="row"><a href="#" class="btn btn-primary btn-sm">edit</a></th>
                            <td>${t38Update[i].pk}</td>
                            <td>${t38Update[i].fields.callSign}</td>
                            <td>${t38Update[i].fields.alt_baro}</td>
                            <td>${t38Update[i].fields.groundSpeed}</td>
                            <td>${t38Update[i].fields.takeoffTime}</td>
                            <td>${t38Update[i].fields.landTime}</td>

                            <td>  
                                <input class="form-check-input" type="checkbox" value="" id="flexCheckDefault">
                                <label class="form-check-label" for="flexCheckDefault">Form Solo</label></td>
                            <td><a href="#" class="btn btn-primary btn-sm btn-danger">355</a></td>
                            </tr>`
                            )
                }
                if (t38Update[i].fields.state == "lost signal") {
                    KEND35LLostSignal.insertAdjacentHTML('beforeend',       
                            `<tr>
                            <th scope="row"><a href="#" class="btn btn-primary btn-sm">edit</a></th>
                            <td>${t38Update[i].pk}</td>
                            <td>${t38Update[i].fields.callSign}</td>
                            <td>${t38Update[i].fields.alt_baro}</td>
                            <td>${t38Update[i].fields.groundSpeed}</td>
                            <td>${t38Update[i].fields.takeoffTime}</td>
                            <td>${t38Update[i].fields.landTime}</td>

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
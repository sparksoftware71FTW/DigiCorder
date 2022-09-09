function loadKEND35R(chatSocket) {

    chatSocket.addEventListener('message', function(e){
        let data = JSON.parse(e.data)

        if(data.type == 't6Update'){

            t6Update = JSON.parse(data.message)

            let KEND35RPattern = document.getElementById('KEND35R In Pattern')
            removeAllChildNodes(KEND35RPattern)
            let KEND35RTaxiing = document.getElementById('KEND35R Taxiing')
            removeAllChildNodes(KEND35RTaxiing)
            let KEND35ROffStation = document.getElementById('KEND35R Off Station')
            removeAllChildNodes(KEND35ROffStation)
            let KEND35RLostSignal = document.getElementById('KEND35R Lost Signal')
            removeAllChildNodes(KEND35RLostSignal)

            for (let i = 0; i < t6Update.length; i++) {

                if (t6Update[i].fields.state == "in pattern") {
                    KEND35RPattern.insertAdjacentHTML('beforeend',       
                            `<tr>
                            <th scope="row"><a href="#" class="btn btn-primary btn-sm">edit</a></th>
                            <td>${t6Update[i].pk}</td>
                            <td>${t6Update[i].fields.callSign}</td>
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
//     while (parent.firstChild) {
//         parent.removeChild(parent.firstChild);
//     }
// }
import { Component } from "@angular/core";
import { MatDialog } from "@angular/material/dialog";

@Component({
	selector: "app-root",
	templateUrl: "./app.component.html",
	styleUrls: ["./app.component.scss"],
})
export class AppComponent {
	title = "codenames-app";

	constructor(private _dialog: MatDialog) {}

	images = [{ path: "/assets/demo.png" }];
}

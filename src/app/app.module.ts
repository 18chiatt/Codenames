import { BrowserModule } from "@angular/platform-browser";
import { NgModule } from "@angular/core";

import { AppRoutingModule } from "./app-routing.module";
import { AppComponent } from "./app.component";
import { BrowserAnimationsModule } from "@angular/platform-browser/animations";
import { MatButtonModule } from "@angular/material/button";
import { MatCardModule } from "@angular/material/card";
import { MatDialogModule } from "@angular/material/dialog";
import { IvyCarouselModule } from "angular-responsive-carousel";
import { NgbModule } from "@ng-bootstrap/ng-bootstrap";

@NgModule({
	declarations: [AppComponent],
	imports: [
		BrowserModule,
		AppRoutingModule,
		BrowserAnimationsModule,
		MatButtonModule,
		MatCardModule,
		MatDialogModule,
		IvyCarouselModule,
		NgbModule,
	],
	providers: [],
	bootstrap: [AppComponent],
})
export class AppModule {}

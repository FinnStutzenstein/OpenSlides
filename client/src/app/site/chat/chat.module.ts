import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';

import { ChatGroupDetailComponent } from './components/chat-group-detail/chat-group-detail.component';
import { ChatGroupListComponent } from './components/chat-group-list/chat-group-list.component';
import { ChatRoutingModule } from './chat-routing.module';
import { SharedModule } from '../../shared/shared.module';

@NgModule({
    imports: [CommonModule, ChatRoutingModule, SharedModule],
    declarations: [ChatGroupListComponent, ChatGroupDetailComponent]
})
export class ChatModule {}

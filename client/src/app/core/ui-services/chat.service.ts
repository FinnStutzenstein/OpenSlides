import { Injectable } from '@angular/core';

import { BehaviorSubject, Observable } from 'rxjs';

import { ChatGroupRepositoryService } from '../repositories/chat/chat-group-repository.service';
import { ConstantsService } from '../core-services/constants.service';
import { OperatorService, Permission } from '../core-services/operator.service';

interface OpenSlidesSettings {
    ENABLE_CHAT: boolean;
}

@Injectable({
    providedIn: 'root'
})
export class ChatService {
    private chatEnabled = false;
    private canSeeSomeChatGroup = false;
    private canManage = false;

    private canSeeChat = new BehaviorSubject<boolean>(false);
    public get canSeeChatObservable(): Observable<boolean> {
        return this.canSeeChat.asObservable();
    }

    public constructor(
        private repo: ChatGroupRepositoryService,
        private operator: OperatorService,
        private constantsService: ConstantsService
    ) {
        this.constantsService.get<OpenSlidesSettings>('Settings').subscribe(settings => {
            this.chatEnabled = settings.ENABLE_CHAT;
            this.update();
        });

        this.repo.getViewModelListBehaviorSubject().subscribe(groups => {
            this.canSeeSomeChatGroup = !!groups && groups.length > 0;
            this.update();
        });

        this.operator.getViewUserObservable().subscribe(() => {
            this.canManage = this.operator.hasPerms(Permission.chatCanManage);
            this.update();
        });
    }

    private update(): void {
        this.canSeeChat.next(this.chatEnabled && (this.canSeeSomeChatGroup || this.canManage));
    }
}
